from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import shutil


class StorageAdapter(ABC):
    """스토리지 추상 인터페이스"""

    @abstractmethod
    async def save_file(self, source_path: str, dest_path: str) -> str:
        """파일 저장"""
        pass

    @abstractmethod
    async def read_file(self, file_path: str) -> bytes:
        """파일 읽기"""
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> bool:
        """파일 삭제"""
        pass

    @abstractmethod
    def exists(self, file_path: str) -> bool:
        """파일 존재 확인"""
        pass

    @abstractmethod
    def get_file_size(self, file_path: str) -> int:
        """파일 크기 조회"""
        pass


class LocalStorageAdapter(StorageAdapter):
    """로컬 파일 시스템 스토리지"""

    def __init__(self, base_path: str = "./workspace"):
        self.base_path = Path(base_path).resolve()
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_full_path(self, file_path: str) -> Path:
        """전체 경로 조회"""
        full_path = (self.base_path / file_path).resolve()
        if full_path != self.base_path and self.base_path not in full_path.parents:
            raise ValueError("Storage path escapes the configured workspace")
        return full_path

    async def save_file(self, source_path: str, dest_path: str) -> str:
        """파일 저장"""
        source = Path(source_path)
        dest = self._get_full_path(dest_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        return str(dest)

    async def read_file(self, file_path: str) -> bytes:
        """파일 읽기"""
        full_path = self._get_full_path(file_path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(full_path, "rb") as f:
            return f.read()

    async def delete_file(self, file_path: str) -> bool:
        """파일 삭제"""
        full_path = self._get_full_path(file_path)
        if full_path.exists():
            full_path.unlink()
            return True
        return False

    def exists(self, file_path: str) -> bool:
        """파일 존재 확인"""
        full_path = self._get_full_path(file_path)
        return full_path.exists()

    def get_file_size(self, file_path: str) -> int:
        """파일 크기 조회"""
        full_path = self._get_full_path(file_path)
        if not full_path.exists():
            return 0
        return full_path.stat().st_size


class NasStorageAdapter(StorageAdapter):
    """NAS 스토리지 (SMB/NFS) - 미구현"""

    def __init__(self, config: dict):
        self.config = config
        self.protocol = config.get("protocol", "smb")
        self.host = config.get("host")
        self.port = config.get("port", 445)
        self.share_name = config.get("share_name")
        self.username = config.get("username")
        self.password = config.get("password")

    async def save_file(self, source_path: str, dest_path: str) -> str:
        raise NotImplementedError("NAS adapter not implemented yet")

    async def read_file(self, file_path: str) -> bytes:
        raise NotImplementedError("NAS adapter not implemented yet")

    async def delete_file(self, file_path: str) -> bool:
        raise NotImplementedError("NAS adapter not implemented yet")

    def exists(self, file_path: str) -> bool:
        raise NotImplementedError("NAS adapter not implemented yet")

    def get_file_size(self, file_path: str) -> int:
        raise NotImplementedError("NAS adapter not implemented yet")
