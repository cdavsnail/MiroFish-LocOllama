import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import sys

# Mock ALL potentially missing dependencies BEFORE they are imported via 'app'
# We need to be aggressive here because app/__init__.py imports many things
for module in [
    'flask', 'flask_cors', 'dotenv', 'pydantic', 'openai',
    'zep_cloud', 'camel', 'fitz', 'charset_normalizer', 'chardet'
]:
    sys.modules[module] = MagicMock()

# Ensure backend is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.utils.file_parser import FileParser, _read_text_with_fallback, split_text_into_chunks

def test_read_text_with_fallback_utf8():
    content = "Hello, world! 你好，世界！"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(content.encode("utf-8"))
        tmp_path = tmp.name

    try:
        result = _read_text_with_fallback(tmp_path)
        assert result == content
    finally:
        os.unlink(tmp_path)

def test_read_text_with_fallback_gbk():
    content = "你好，世界！"
    encoded_content = content.encode("gbk")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(encoded_content)
        tmp_path = tmp.name

    # Mock charset_normalizer to return GBK
    mock_best = MagicMock()
    mock_best.encoding = 'gbk'
    sys.modules["charset_normalizer"].from_bytes.return_value.best.return_value = mock_best

    try:
        result = _read_text_with_fallback(tmp_path)
        assert result == content
    finally:
        os.unlink(tmp_path)

def test_file_parser_extract_text_txt():
    content = "Test content"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
        tmp.write(content.encode("utf-8"))
        tmp_path = tmp.name

    try:
        result = FileParser.extract_text(tmp_path)
        assert result == content
    finally:
        os.unlink(tmp_path)

def test_file_parser_extract_text_md():
    content = "# Heading\nContent"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as tmp:
        tmp.write(content.encode("utf-8"))
        tmp_path = tmp.name

    try:
        result = FileParser.extract_text(tmp_path)
        assert result == content
    finally:
        os.unlink(tmp_path)

def test_file_parser_extract_text_pdf_mocked():
    # Mock fitz (PyMuPDF)
    mock_fitz = sys.modules["fitz"]
    mock_doc = MagicMock()
    mock_page1 = MagicMock()
    mock_page2 = MagicMock()

    mock_page1.get_text.return_value = "Page 1 content"
    mock_page2.get_text.return_value = "Page 2 content"
    mock_doc.__iter__.return_value = [mock_page1, mock_page2]
    mock_doc.__enter__.return_value = mock_doc
    mock_fitz.open.return_value = mock_doc

    # We need a dummy file that exists
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp_path = tmp.name

    try:
        result = FileParser.extract_text(tmp_path)
        assert "Page 1 content" in result
        assert "Page 2 content" in result
        assert "\n\n" in result
    finally:
        os.unlink(tmp_path)

def test_file_parser_extract_text_not_found():
    with pytest.raises(FileNotFoundError):
        FileParser.extract_text("non_existent_file.txt")

def test_file_parser_extract_text_unsupported():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".exe") as tmp:
        tmp_path = tmp.name

    try:
        with pytest.raises(ValueError, match="不支持的文件格式"):
            FileParser.extract_text(tmp_path)
    finally:
        os.unlink(tmp_path)

def test_extract_from_multiple():
    content1 = "Content 1"
    content2 = "Content 2"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp1, \
         tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp2:
        tmp1.write(content1.encode("utf-8"))
        tmp2.write(content2.encode("utf-8"))
        path1, path2 = tmp1.name, tmp2.name

    try:
        result = FileParser.extract_from_multiple([path1, path2])
        assert "=== 文档 1" in result
        assert content1 in result
        assert "=== 文档 2" in result
        assert content2 in result
    finally:
        os.unlink(path1)
        os.unlink(path2)

def test_extract_from_multiple_with_failure():
    content1 = "Content 1"
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp1:
        tmp1.write(content1.encode("utf-8"))
        path1 = tmp1.name

    path2 = "non_existent.txt"

    try:
        result = FileParser.extract_from_multiple([path1, path2])
        assert content1 in result
        assert "提取失败" in result
        assert "non_existent.txt" in result
    finally:
        os.unlink(path1)

def test_split_text_into_chunks_basic():
    text = "a" * 100
    chunks = split_text_into_chunks(text, chunk_size=30, overlap=10)
    assert len(chunks) == 5
    for chunk in chunks:
        assert len(chunk) <= 30

def test_split_text_into_chunks_sentence_boundary():
    text = "句子一。句子二！句子三？结尾。"
    chunks = split_text_into_chunks(text, chunk_size=6, overlap=2)
    assert "句子一。" in chunks[0]
    assert "句子二！" in chunks[1]

def test_split_text_into_chunks_empty():
    assert split_text_into_chunks("") == []
    assert split_text_into_chunks("   ") == []

def test_split_text_into_chunks_small():
    text = "Hello world"
    chunks = split_text_into_chunks(text, chunk_size=100)
    assert chunks == [text]
