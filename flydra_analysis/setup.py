from setuptools import setup, find_packages
from distutils.core import Extension  # actually monkey-patched by setuptools
from Cython.Build import cythonize

import numpy as np

from io import open
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

INSTALL_REQUIRES = [
    # these are Depends in stdeb.cfg. (The Build-Depends must be already installed.)
    "flydra_core",
    "numpy",
    "scipy",
    "cgkit1",
    "nose",
    "h5py",
    "aggdraw",
    "pandas",
    "sympy",
    "docopt",
    "CherryPy",
    "pymvg",
    "benu",
    "motmot.ufmf",
    "adskalman",
    "matplotlib",
    "progressbar",
    "tables",
    "six",
]

ext_modules = []

ext_modules.append(
    Extension(
        name="flydra_analysis.a2.fastfinder_help",
        sources=["flydra_analysis/a2/fastfinder_help.pyx"],
        include_dirs=[np.get_include()],
    )
)

setup(
    name="flydra_analysis",
    version="0.7.10",  # keep in sync with flydra_analysis/version.py
    author="Andrew Straw",
    author_email="strawman@astraw.com",
    url="https://github.com/strawlab/flydra",
    description="flydra analysis tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    test_suite="nose.collector",
    ext_modules=cythonize(ext_modules),
    entry_points={
        "console_scripts": [
            # analysis - re-kalmanize
            "flydra_kalmanize = flydra_analysis.kalmanize:main",
            # analysis - ufmf care and feeding
            "flydra_analysis_auto_discover_ufmfs = flydra_analysis.a2.auto_discover_ufmfs:main",
            "flydra_analysis_montage_ufmfs = flydra_analysis.a2.montage_ufmfs:main",
            "flydra_analysis_retrack_movies = flydra_analysis.a2.retrack_movies:main",
            # analysis - generate movies with tracking overlays (uses fmfs or ufmfs)
            "flydra_analysis_overlay_kalman_movie = flydra_analysis.a2.overlay_kalman_movie:main",
            # analysis - .h5 file care and feeding
            "flydra_analysis_check_sync = flydra_analysis.kalmanize:check_sync",
            "flydra_analysis_print_h5_info = flydra_analysis.a2.h5_info:cmdline",
            "flydra_analysis_filter_kalman_data = flydra_analysis.analysis.flydra_analysis_filter_kalman_data:main",
            "flydra_analysis_h5_shorten = flydra_analysis.a2.h5_shorten:main",
            "flydra_analysis_check_mainbrain_h5_contiguity = flydra_analysis.a2.check_mainbrain_h5_contiguity:main",
            "flydra_analysis_get_clock_sync = flydra_analysis.a2.get_clock_sync:main",
            "flydra_analysis_get_2D_image_latency = flydra_analysis.a2.get_2D_image_latency:main",
            "flydra_analysis_get_2D_image_latency_plot = flydra_analysis.a2.get_2D_image_latency_plot:main",
            # timestamp conversion
            "flydra_analysis_frame2timestamp = flydra_analysis.analysis.result_utils:frame2timestamp_command",
            "flydra_analysis_timestamp2frame = flydra_analysis.analysis.result_utils:timestamp2frame_command",
            # analysis - not yet classified
            "flydra_analysis_convert_to_mat = flydra_analysis.analysis.flydra_analysis_convert_to_mat:main",
            "flydra_analysis_plot_clock_drift = flydra_analysis.analysis.flydra_analysis_plot_clock_drift:main",
            "flydra_analysis_plot_kalman_2d = flydra_analysis.a2.plot_kalman_2d:main",
            "flydra_analysis_plot_summary = flydra_analysis.a2.plot_summary:main",
            "flydra_analysis_plot_timeseries_2d_3d = flydra_analysis.a2.plot_timeseries_2d_3d:main",
            "flydra_analysis_plot_timeseries_3d = flydra_analysis.a2.plot_timeseries:main",
            "flydra_analysis_plot_top_view = flydra_analysis.a2.plot_top_view:main",
            "flydra_analysis_print_camera_summary = flydra_analysis.analysis.flydra_analysis_print_camera_summary:main",
            "flydra_analysis_save_movies_overlay = flydra_analysis.a2.save_movies_overlay:main",
            "flydra_images_export = flydra_analysis.a2.flydra_images_export:main",
            "kdviewer = flydra_analysis.a2.kdviewer:main",
            "kdmovie_saver = flydra_analysis.a2.kdmovie_saver:main",
            "flydra_analysis_data2smoothed = flydra_analysis.a2.data2smoothed:main",
            "flydra_analysis_export_flydra_hdf5 = flydra_analysis.a2.data2smoothed:export_flydra_hdf5",
            "flydra_textlog2csv = flydra_analysis.a2.flydra_textlog2csv:main",
            "flydra_analysis_print_kalmanize_makefile_location = flydra_analysis.a2.print_kalmanize_makefile_location:main",
            "flydra_analysis_calculate_reprojection_errors = flydra_analysis.a2.calculate_reprojection_errors:main",
            "flydra_analysis_retrack_reuse_data_association = flydra_analysis.a2.retrack_reuse_data_association:main",
            "flydra_analysis_calculate_skipped_frames = flydra_analysis.a2.calculate_skipped_frames:main",
            "flydra_analysis_plot_skipped_frames = flydra_analysis.a2.plot_skipped_frames:main",
            # analysis - image based orientation
            "flydra_analysis_image_based_orientation = flydra_analysis.a2.image_based_orientation:main",
            "flydra_analysis_orientation_ekf_fitter = flydra_analysis.a2.orientation_ekf_fitter:main",
            "flydra_analysis_orientation_ekf_plot = flydra_analysis.a2.orientation_ekf_plot:main",
            "flydra_analysis_orientation_is_fit = flydra_analysis.a2.orientation_ekf_fitter:is_orientation_fit_sysexit",
            # camera calibration
            "flydra_analysis_calibration_align_gui = flydra_analysis.a2.calibration_align_gui:main",
            "flydra_analysis_generate_recalibration = flydra_analysis.analysis.flydra_analysis_generate_recalibration:main",
            "flydra_analysis_plot_calibration_input = flydra_analysis.a2.plot_calibration_input:main",
            "flydra_analysis_calibration_to_xml = flydra_analysis.a2.calibration_to_xml:main",
            "flydra_analysis_water_surface_align = flydra_analysis.a2.water_surface_align:main",
            "flydra_analysis_plot_camera_positions = flydra_analysis.a2.plot_camera_positions:main",
            # ROS pointcloud stuff
            "flydra_analysis_rosbag2flydrah5 = flydra_analysis.a2.rosbag2flydrah5:main",
            # testing
            "flydra_test_commands = flydra_analysis.test_commands:main",
        ],
        "flydra_analysis.kdviewer.plugins": [
            "default = flydra_analysis.a2.conditions_draw:default",
            "mama07 = flydra_analysis.a2.conditions_draw:mama07",
            "mama20080414 = flydra_analysis.a2.conditions_draw:mama20080414",
            "mama20080501 = flydra_analysis.a2.conditions_draw:mama20080501",
            "hum07 = flydra_analysis.a2.conditions_draw:hum07",
            "wt0803 = flydra_analysis.a2.conditions_draw:wt0803",
        ],
    },
    package_data={
        "flydra_analysis.a2": [
            "kdmovie_saver_default_path.kmp",
            "sample_*.h5",
            "sample_*.mat",
            "sample_calibration.xml",
            "Makefile.kalmanize",
        ],
    },
    install_requires=INSTALL_REQUIRES,
)
