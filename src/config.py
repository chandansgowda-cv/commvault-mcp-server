# --------------------------------------------------------------------------
# Copyright Commvault Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------

"""
Configuration module for Commvault MCP Server.

This module handles all configuration-related functionality including
environment variable management and server settings.
"""

import sys
from dataclasses import dataclass
from typing import Optional

from src.logger import logger
from src.utils import get_env_var


@dataclass
class ServerConfig:
    transport_mode: str
    host: Optional[str] = None
    port: Optional[int] = None
    path: Optional[str] = None
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.transport_mode not in ["stdio", "streamable-http", "sse"]:
            raise ValueError(f"Invalid transport mode: {self.transport_mode}")
        
        if self.transport_mode != "stdio":
            if not all([self.host, self.port, self.path]):
                raise ValueError("Host, port, and path are required for non-stdio transport modes")


class ConfigManager:
    @staticmethod
    def load_config() -> ServerConfig:
        """
        Load server configuration from environment variables.
        """
        try:
            transport_mode = get_env_var("MCP_TRANSPORT_MODE")
            
            # Only load network config for non-stdio modes
            if transport_mode != "stdio":
                host = get_env_var("MCP_HOST")
                port = int(get_env_var("MCP_PORT"))
                path = get_env_var("MCP_PATH")
                config = ServerConfig(
                    transport_mode=transport_mode,
                    host=host,
                    port=port,
                    path=path
                )
            else:
                config = ServerConfig(transport_mode=transport_mode)
            
            logger.info(f"Configuration loaded successfully: transport={transport_mode}")
            return config
            
        except (ValueError, TypeError) as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error loading configuration: {e}")
            sys.exit(1)


# Server constants
SERVER_NAME = "Commvault MCP Server"
SERVER_INSTRUCTIONS = "You can use this server to interact with Commvault Product"
