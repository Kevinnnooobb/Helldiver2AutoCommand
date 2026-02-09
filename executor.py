"""
战备指令执行器
Executes stratagem commands by simulating keyboard input.
"""

import time
import logging

logger = logging.getLogger(__name__)


def execute_stratagem(stratagem, config, keyboard_module=None):
    """
    Execute a stratagem command sequence by simulating key presses.

    Args:
        stratagem: A stratagem dict with a 'command' list of direction arrows.
        config: Configuration dict with 'key_bindings', 'stratagem_key', 'key_delay'.
        keyboard_module: The keyboard module to use (for dependency injection/testing).
                         If None, imports the 'keyboard' package.
    """
    if keyboard_module is None:
        try:
            import keyboard as kb
            keyboard_module = kb
        except ImportError:
            logger.error(
                "keyboard 模块未安装。请运行: pip install keyboard"
            )
            raise

    key_bindings = config["key_bindings"]
    stratagem_key = config["stratagem_key"]
    key_delay = config.get("key_delay", 0.05)
    command = stratagem["command"]

    logger.info(
        "执行战备: %s (%s) - 指令: %s",
        stratagem["name"],
        stratagem["model"],
        "".join(command),
    )

    # Hold down the stratagem activation key
    keyboard_module.press(stratagem_key)
    time.sleep(key_delay)

    try:
        for direction in command:
            key = key_bindings.get(direction, direction)
            keyboard_module.press(key)
            time.sleep(key_delay)
            keyboard_module.release(key)
            time.sleep(key_delay)
    finally:
        # Always release the stratagem key
        keyboard_module.release(stratagem_key)

    logger.info("战备指令执行完成: %s", stratagem["name"])
