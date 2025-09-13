# Test configuration and fixtures for TMIN package
import pytest
import numpy as np
from tmin.core_dev import PIPE


@pytest.fixture
def sample_pipe():
    """Create a standard pipe instance for testing"""
    return PIPE(
        pressure=150.0,
        nps=2.0,
        schedule=40,
        pressure_class=300,
        metallurgy="Intermediate/Low CS",
        yield_stress=30000,
        corrosion_rate=5.0
    )


@pytest.fixture
def sample_pipe_ss():
    """Create a stainless steel pipe instance for testing"""
    return PIPE(
        pressure=200.0,
        nps=1.5,
        schedule=80,
        pressure_class=600,
        metallurgy="SS 316/316L",
        yield_stress=25000,
        corrosion_rate=2.0
    )


@pytest.fixture
def sample_pipe_elbow():
    """Create an elbow pipe instance for testing"""
    return PIPE(
        pressure=100.0,
        nps=3.0,
        schedule=40,
        pressure_class=150,
        metallurgy="Intermediate/Low CS",
        yield_stress=30000,
        pipe_config="90LR - Inner Elbow",
        corrosion_rate=3.0
    )
