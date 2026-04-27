import os
import json
import pytest
from unittest.mock import patch, MagicMock

from app.services.simulation_manager import (
    SimulationManager,
    SimulationState,
    SimulationStatus,
    PlatformType
)

@pytest.fixture
def temp_sim_dir(tmp_path):
    # Use tmp_path for SimulationManager's data dir
    with patch("app.services.simulation_manager.SimulationManager.SIMULATION_DATA_DIR", str(tmp_path)):
        yield str(tmp_path)

@pytest.fixture
def sim_manager(temp_sim_dir):
    return SimulationManager()

def test_init_creates_dir(temp_sim_dir):
    manager = SimulationManager()
    assert os.path.exists(temp_sim_dir)
    assert manager._simulations == {}

def test_get_simulation_dir(sim_manager, temp_sim_dir):
    sim_id = "test_sim_123"
    dir_path = sim_manager._get_simulation_dir(sim_id)
    assert os.path.exists(dir_path)
    assert dir_path == os.path.join(temp_sim_dir, sim_id)

def test_create_simulation(sim_manager):
    project_id = "proj_1"
    graph_id = "graph_1"

    state = sim_manager.create_simulation(project_id, graph_id)

    assert state.project_id == project_id
    assert state.graph_id == graph_id
    assert state.status == SimulationStatus.CREATED
    assert state.enable_twitter is True
    assert state.enable_reddit is True
    assert state.simulation_id.startswith("sim_")

    # Check if state is cached
    assert state.simulation_id in sim_manager._simulations

def test_save_and_load_simulation_state(sim_manager, temp_sim_dir):
    sim_id = "test_sim_456"
    state = SimulationState(
        simulation_id=sim_id,
        project_id="proj_2",
        graph_id="graph_2"
    )

    # Save state
    sim_manager._save_simulation_state(state)

    # Check if file is created
    state_file = os.path.join(temp_sim_dir, sim_id, "state.json")
    assert os.path.exists(state_file)

    # Load state directly from file bypassing cache
    sim_manager._simulations = {}
    loaded_state = sim_manager._load_simulation_state(sim_id)

    assert loaded_state is not None
    assert loaded_state.simulation_id == sim_id
    assert loaded_state.project_id == "proj_2"
    assert loaded_state.graph_id == "graph_2"

def test_load_simulation_state_not_found(sim_manager):
    loaded_state = sim_manager._load_simulation_state("non_existent_sim")
    assert loaded_state is None

def test_list_simulations(sim_manager, temp_sim_dir):
    # Create two simulations
    state1 = sim_manager.create_simulation("proj_1", "graph_1")
    state2 = sim_manager.create_simulation("proj_1", "graph_2")
    state3 = sim_manager.create_simulation("proj_2", "graph_3")

    # Create some noise in the directory
    os.makedirs(os.path.join(temp_sim_dir, ".DS_Store"), exist_ok=True)
    open(os.path.join(temp_sim_dir, "not_a_dir.txt"), 'w').close()

    # List all
    all_sims = sim_manager.list_simulations()
    assert len(all_sims) == 3

    # List by project
    proj_1_sims = sim_manager.list_simulations(project_id="proj_1")
    assert len(proj_1_sims) == 2
    assert all(s.project_id == "proj_1" for s in proj_1_sims)


@patch("app.services.simulation_manager.ZepEntityReader")
@patch("app.services.simulation_manager.OasisProfileGenerator")
@patch("app.services.simulation_manager.SimulationConfigGenerator")
def test_prepare_simulation_success(MockConfigGen, MockProfileGen, MockZepReader, sim_manager, temp_sim_dir):
    # Setup mocks
    mock_zep_reader = MockZepReader.return_value
    mock_filtered_entities = MagicMock()
    mock_filtered_entities.filtered_count = 2
    mock_filtered_entities.entity_types = ["type1", "type2"]
    mock_filtered_entities.entities = [{"name": "A"}, {"name": "B"}]
    mock_zep_reader.filter_defined_entities.return_value = mock_filtered_entities

    mock_profile_gen = MockProfileGen.return_value
    mock_profile_gen.generate_profiles_from_entities.return_value = [{"id": 1}, {"id": 2}]

    mock_config_gen = MockConfigGen.return_value
    mock_sim_params = MagicMock()
    mock_sim_params.to_json.return_value = '{"config": "value"}'
    mock_sim_params.generation_reasoning = "test reasoning"
    mock_config_gen.generate_config.return_value = mock_sim_params

    # Create simulation
    state = sim_manager.create_simulation("proj_1", "graph_1")
    sim_id = state.simulation_id

    # Progress callback mock
    progress_callback = MagicMock()

    # Call prepare_simulation
    updated_state = sim_manager.prepare_simulation(
        simulation_id=sim_id,
        simulation_requirement="test req",
        document_text="test doc",
        defined_entity_types=["type1"],
        use_llm_for_profiles=False,
        progress_callback=progress_callback
    )

    # Assertions on state
    assert updated_state.status == SimulationStatus.READY
    assert updated_state.entities_count == 2
    assert updated_state.profiles_count == 2
    assert updated_state.config_generated is True
    assert updated_state.config_reasoning == "test reasoning"

    # Verify mocks were called correctly
    mock_zep_reader.filter_defined_entities.assert_called_once()
    mock_profile_gen.generate_profiles_from_entities.assert_called_once()
    mock_profile_gen.save_profiles.assert_called()  # Should be called for Twitter and Reddit if both enabled
    assert mock_profile_gen.save_profiles.call_count == 2
    mock_config_gen.generate_config.assert_called_once()

    # Verify files were created
    sim_dir = sim_manager._get_simulation_dir(sim_id)
    assert os.path.exists(os.path.join(sim_dir, "simulation_config.json"))

    # Verify progress callback was called multiple times
    assert progress_callback.call_count > 0

@patch("app.services.simulation_manager.ZepEntityReader")
def test_prepare_simulation_no_entities(MockZepReader, sim_manager, temp_sim_dir):
    # Setup mocks
    mock_zep_reader = MockZepReader.return_value
    mock_filtered_entities = MagicMock()
    mock_filtered_entities.filtered_count = 0
    mock_filtered_entities.entity_types = []
    mock_filtered_entities.entities = []
    mock_zep_reader.filter_defined_entities.return_value = mock_filtered_entities

    # Create simulation
    state = sim_manager.create_simulation("proj_1", "graph_1")
    sim_id = state.simulation_id

    # Call prepare_simulation
    updated_state = sim_manager.prepare_simulation(
        simulation_id=sim_id,
        simulation_requirement="test req",
        document_text="test doc"
    )

    # Assertions on state
    assert updated_state.status == SimulationStatus.FAILED
    assert updated_state.error == "没有找到符合条件的实体，请检查图谱是否正确构建"

def test_prepare_simulation_not_found(sim_manager):
    with pytest.raises(ValueError, match="模拟不存在"):
        sim_manager.prepare_simulation(
            simulation_id="non_existent",
            simulation_requirement="req",
            document_text="doc"
        )

def test_get_profiles_success(sim_manager, temp_sim_dir):
    state = sim_manager.create_simulation("proj_1", "graph_1")
    sim_id = state.simulation_id
    sim_dir = sim_manager._get_simulation_dir(sim_id)

    # Create a mock profiles json file
    profiles_data = [{"name": "Agent1"}, {"name": "Agent2"}]
    with open(os.path.join(sim_dir, "reddit_profiles.json"), "w") as f:
        json.dump(profiles_data, f)

    profiles = sim_manager.get_profiles(sim_id, platform="reddit")
    assert len(profiles) == 2
    assert profiles[0]["name"] == "Agent1"

def test_get_profiles_not_found(sim_manager, temp_sim_dir):
    state = sim_manager.create_simulation("proj_1", "graph_1")
    sim_id = state.simulation_id

    profiles = sim_manager.get_profiles(sim_id, platform="reddit")
    assert profiles == []

def test_get_profiles_simulation_not_found(sim_manager):
    with pytest.raises(ValueError, match="模拟不存在"):
        sim_manager.get_profiles("non_existent")

def test_get_simulation_config_success(sim_manager, temp_sim_dir):
    state = sim_manager.create_simulation("proj_1", "graph_1")
    sim_id = state.simulation_id
    sim_dir = sim_manager._get_simulation_dir(sim_id)

    config_data = {"key": "value"}
    with open(os.path.join(sim_dir, "simulation_config.json"), "w") as f:
        json.dump(config_data, f)

    config = sim_manager.get_simulation_config(sim_id)
    assert config is not None
    assert config["key"] == "value"

def test_get_simulation_config_not_found(sim_manager, temp_sim_dir):
    state = sim_manager.create_simulation("proj_1", "graph_1")
    sim_id = state.simulation_id

    config = sim_manager.get_simulation_config(sim_id)
    assert config is None

def test_get_run_instructions(sim_manager, temp_sim_dir):
    state = sim_manager.create_simulation("proj_1", "graph_1")
    sim_id = state.simulation_id

    instructions = sim_manager.get_run_instructions(sim_id)

    assert "simulation_dir" in instructions
    assert "scripts_dir" in instructions
    assert "config_file" in instructions
    assert "commands" in instructions
    assert "instructions" in instructions

    # Verify paths are absolute/correctly formed
    sim_dir = sim_manager._get_simulation_dir(sim_id)
    assert instructions["simulation_dir"] == sim_dir
    assert instructions["config_file"] == os.path.join(sim_dir, "simulation_config.json")

    commands = instructions["commands"]
    assert "twitter" in commands
    assert "reddit" in commands
    assert "parallel" in commands
