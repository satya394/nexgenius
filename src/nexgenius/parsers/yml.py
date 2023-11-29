# Path: src/nexgenius/parsers/yml.py

import inspect
import logging
import logging.config
from copy import deepcopy
from functools import reduce
from importlib import import_module
from operator import getitem
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, TypeVar, Union

import yaml

logger = logging.getLogger(__name__)

class YAMLParser:
    def __init__(self, config_fname: Union[str, Path] = None, config_dir: Path=None) -> None:
        if config_dir:
            self.config_dir = Path(config_dir).resolve()
        else:
            self.config_dir = Path(__file__).parents[3].resolve() / "conf"
        
        # Default configuration
        self.config_fname = config_fname.strip().lower() if config_fname else "config"

    def _check_attr(self, **kwargs):
        updated_kwargs = {
            key: getattr(self, key, None) if val is None else val for key, val in kwargs.items()
        }
    
    def _get_config_params(self, section_name:str = None, config_fname: str=None) -> Dict:
        (config_fname, ) = self._check_attr(config_fname=config_fname)
        config_fpath = self.config_dir / f"{config_fname}.yml"
        with open(config_fpath, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        if isinstance(section_name, str):
            section_name = section_name.split(".")
        elif section_name is None:
            raise ValueError("`section_name` must be provided")
        elif not isinstance(section_name, (str, list)):
            raise TypeError("`section_name` must be str or list")

        try:
            return reduce(getitem, section_name, config)
        except:
            raise ValueError(f"Section name '{section_name}' not found in config file")
    
    def get_model_class(self, config_fname: str, model: Union[TypeVar, str]=None) -> TypeVar:
        if inspect.isclass(model):
            package_name = model.__module__.split(".")[0]
            return package_name, model
        elif isinstance(model, str):
            try:
                module_name, class_name = model.rsplit(".", 1)
            except ValueError as err:
                module_name, class_name = self._get_config_params(config_fname, f"models.{model}")).rsplit(".", 1)

            module = import_module(module_name)
            model_class = getattr(module, class_name)
            package_name = module_name.split(".")[0]
            return package_name, model_class
        else:
            raise TypeError("`model` must be a class or str")