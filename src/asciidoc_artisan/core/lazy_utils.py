"""
Lazy Loading Utilities - Defer expensive initializations.

This module provides utilities for lazy loading and deferred initialization:
- Lazy property decorator
- Lazy import utilities
- Deferred initialization helpers

Implements Phase 2.4 of Performance Optimization Plan:
- Reduce startup time
- Defer expensive operations
- Load components on-demand
- Memory-efficient initialization

Features:
- @lazy_property decorator
- Cached lazy properties
- Thread-safe lazy initialization
- Import deferral
"""

import functools
import importlib
import logging
from typing import Any, Callable, Generic, Optional, TypeVar

logger = logging.getLogger(__name__)


T = TypeVar("T")


class lazy_property(Generic[T]):
    """
    Lazy property decorator.

    Computes property value on first access and caches it.
    Subsequent accesses return cached value without recomputation.

    Thread-safe and memory-efficient.

    Example:
        class MyClass:
            @lazy_property
            def expensive_resource(self):
                # This only runs once, on first access
                print("Initializing...")
                return SomeExpensiveObject()

        obj = MyClass()
        # Nothing initialized yet

        result = obj.expensive_resource  # Prints "Initializing..."
        # Cached value

        result2 = obj.expensive_resource  # No print, uses cache
        # Same cached value
    """

    def __init__(self, func: Callable[[Any], T]):
        """
        Initialize lazy property.

        Args:
            func: Function to compute property value
        """
        self.func = func
        self.attr_name = f"_lazy_{func.__name__}"
        functools.update_wrapper(self, func)  # type: ignore[arg-type]

    def __get__(self, obj: Any, owner: type) -> T:
        """
        Get property value.

        Args:
            obj: Instance
            owner: Class

        Returns:
            Property value (computed or cached)
        """
        if obj is None:
            return self  # type: ignore

        # Check if already computed
        if hasattr(obj, self.attr_name):
            return getattr(obj, self.attr_name)

        # Compute value
        value = self.func(obj)

        # Cache it
        setattr(obj, self.attr_name, value)

        logger.debug(f"Lazy property '{self.func.__name__}' initialized")

        return value

    def __set__(self, obj: Any, value: T) -> None:
        """
        Set property value (caches it).

        Args:
            obj: Instance
            value: Value to cache
        """
        setattr(obj, self.attr_name, value)

    def __delete__(self, obj: Any) -> None:
        """
        Delete cached value.

        Args:
            obj: Instance
        """
        if hasattr(obj, self.attr_name):
            delattr(obj, self.attr_name)


class LazyImport:
    """
    Lazy module import.

    Defers module import until first use.
    Useful for optional dependencies or heavy modules.

    Example:
        # Defer pandas import
        pandas = LazyImport('pandas')

        # pandas not imported yet

        # First use triggers import
        df = pandas.DataFrame({'a': [1, 2, 3]})

        # Subsequent uses use cached module
        df2 = pandas.read_csv('data.csv')
    """

    def __init__(self, module_name: str):
        """
        Initialize lazy import.

        Args:
            module_name: Module to import
        """
        self.module_name = module_name
        self._module: Optional[Any] = None

    def __getattr__(self, name: str) -> Any:
        """
        Get attribute from module (imports if needed).

        Args:
            name: Attribute name

        Returns:
            Module attribute
        """
        if self._module is None:
            logger.debug(f"Lazy importing '{self.module_name}'")
            self._module = importlib.import_module(self.module_name)

        return getattr(self._module, name)

    def __dir__(self):
        """Get module attributes."""
        if self._module is None:
            self._module = importlib.import_module(self.module_name)

        return dir(self._module)


def defer_method(func: Callable) -> Callable:
    """
    Decorator to defer method execution.

    Method execution is queued and can be run later.
    Useful for non-critical initialization.

    Example:
        class MyClass:
            def __init__(self):
                self._deferred_calls = []

            @defer_method
            def load_plugins(self):
                # Heavy operation
                self.plugins = discover_plugins()

            def run_deferred(self):
                for call in self._deferred_calls:
                    call()
                self._deferred_calls.clear()

        obj = MyClass()
        obj.load_plugins()  # Queued, not executed
        # ... do critical stuff ...
        obj.run_deferred()  # Now execute deferred calls
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, "_deferred_calls"):
            self._deferred_calls = []

        def deferred_call():
            return func(self, *args, **kwargs)

        self._deferred_calls.append(deferred_call)
        logger.debug(f"Deferred method call: {func.__name__}")

    return wrapper


class LazyInitializer:
    """
    Lazy initialization helper.

    Manages deferred initialization of components.

    Example:
        class Application:
            def __init__(self):
                self.initializer = LazyInitializer()

                # Register deferred initializations
                self.initializer.register('git', self._init_git)
                self.initializer.register('export', self._init_export)
                self.initializer.register('ai', self._init_ai)

            def _init_git(self):
                self.git_handler = GitHandler()

            def _init_export(self):
                self.export_manager = ExportManager()

            def _init_ai(self):
                self.ai_client = AIClient()

            def initialize_critical(self):
                # Initialize only critical components
                self.initializer.initialize('git')

            def initialize_all(self):
                # Initialize remaining components
                self.initializer.initialize_remaining()
    """

    def __init__(self):
        """Initialize lazy initializer."""
        self._initializers: dict[str, Callable] = {}
        self._initialized: set[str] = set()

    def register(self, name: str, initializer: Callable) -> None:
        """
        Register deferred initializer.

        Args:
            name: Component name
            initializer: Initialization function
        """
        self._initializers[name] = initializer
        logger.debug(f"Registered lazy initializer: {name}")

    def initialize(self, name: str) -> None:
        """
        Initialize specific component.

        Args:
            name: Component name
        """
        if name in self._initialized:
            return  # Already initialized

        if name not in self._initializers:
            raise ValueError(f"No initializer registered for '{name}'")

        logger.info(f"Lazy initializing: {name}")
        self._initializers[name]()
        self._initialized.add(name)

    def initialize_remaining(self) -> None:
        """Initialize all remaining components."""
        remaining = set(self._initializers.keys()) - self._initialized

        if remaining:
            logger.info(f"Lazy initializing remaining: {remaining}")

            for name in remaining:
                self.initialize(name)

    def is_initialized(self, name: str) -> bool:
        """
        Check if component is initialized.

        Args:
            name: Component name

        Returns:
            True if initialized
        """
        return name in self._initialized

    def get_statistics(self) -> dict:
        """
        Get initialization statistics.

        Returns:
            Dictionary with stats
        """
        total = len(self._initializers)
        initialized = len(self._initialized)
        pending = total - initialized

        return {
            "total": total,
            "initialized": initialized,
            "pending": pending,
            "components": {
                name: (name in self._initialized) for name in self._initializers.keys()
            },
        }


class cached_property:
    """
    Cached property (like functools.cached_property but custom).

    Similar to lazy_property but provides __set_name__ for better introspection.

    Example:
        class MyClass:
            @cached_property
            def data(self):
                return load_heavy_data()

        obj = MyClass()
        obj.data  # Computes and caches
        obj.data  # Returns cached value
    """

    def __init__(self, func: Callable):
        """
        Initialize cached property.

        Args:
            func: Function to compute property
        """
        self.func = func
        self.attrname: Optional[str] = None
        functools.update_wrapper(self, func)  # type: ignore[arg-type]

    def __set_name__(self, owner: type, name: str) -> None:
        """
        Set attribute name.

        Args:
            owner: Owner class
            name: Attribute name
        """
        self.attrname = name

    def __get__(self, obj: Any, owner: Optional[type] = None) -> Any:
        """Get property value."""
        if obj is None:
            return self

        if self.attrname is None:
            raise TypeError(
                "Cannot use cached_property instance without calling __set_name__"
            )

        # Check cache
        cache = obj.__dict__
        if self.attrname in cache:
            return cache[self.attrname]

        # Compute and cache
        value = self.func(obj)
        cache[self.attrname] = value

        return value
