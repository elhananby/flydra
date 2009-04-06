from __future__ import with_statement
import motmot.ufmf.ufmf as ufmf_mod
import sys, os, tempfile, re, contextlib, warnings
from optparse import OptionParser
import flydra.a2.auto_discover_ufmfs as auto_discover_ufmfs
import numpy as np
import tables
import flydra.a2.utils as utils
import flydra.analysis.result_utils as result_utils
import scipy.misc
import subprocess

from tables_tools import openFileSafe

ufmf_fname_regex = re.compile(r'small_([0-9]+)_([0-9]+)_(.*)')
def get_cam_id_from_ufmf_fname(ufmf_fname):
    a = os.path.split( ufmf_fname )[-1]
    b = os.path.splitext(a)[0]
    matchobj = ufmf_fname_regex.search(b)
    date, time, cam_id= matchobj.groups()
    return cam_id

def iterate_frames(h5_filename,
                   ufmf_fnames,
                   white_background=False,
                   max_n_frames = None,
                   start = None,
                   stop = None,
                   ):
    """yield frame-by-frame data"""

    # First pass over .ufmf files: get intersection of timestamps
    first_ufmf_ts = -np.inf
    last_ufmf_ts = np.inf
    ufmfs = {}
    cam_ids = []
    for ufmf_fname in ufmf_fnames:
        cam_id = get_cam_id_from_ufmf_fname(ufmf_fname)
        cam_ids.append( cam_id )
        kwargs = {}
        if white_background:
            kwargs['use_conventional_named_mean_fmf']=False
        ufmf = ufmf_mod.FlyMovieEmulator(ufmf_fname,
                                         white_background=white_background,
                                         **kwargs)
        tss = ufmf.get_all_timestamps()
        ufmfs[ufmf_fname] = (ufmf, cam_id, tss)
        min_ts = np.min(tss)
        max_ts = np.max(tss)
        if min_ts > first_ufmf_ts:
            first_ufmf_ts = min_ts
        if max_ts < last_ufmf_ts:
            last_ufmf_ts = max_ts

    assert first_ufmf_ts < last_ufmf_ts, ".ufmf files don't all overlap in time"

    ufmf_fnames.sort()
    cam_ids.sort()

    with openFileSafe( h5_filename, mode='r' ) as h5:
        camn2cam_id, cam_id2camns = result_utils.get_caminfo_dicts(h5)
        parsed = result_utils.read_textlog_header(h5)
        flydra_version = parsed.get('flydra_version',None)
        if flydra_version is not None and flydra_version >= '0.4.45':
            # camnode.py saved timestamps into .ufmf file given by
            # time.time() (camn_receive_timestamp). Compare with
            # mainbrain's data2d_distorted column
            # 'cam_received_timestamp'.
            old_camera_timestamp_source = False
            timestamp_name = 'cam_received_timestamp'
        else:
            # camnode.py saved timestamps into .ufmf file given by
            # camera driver. Compare with mainbrain's data2d_distorted
            # column 'timestamp'.
            old_camera_timestamp_source = True
            timestamp_name = 'timestamp'

        h5_data = h5.root.data2d_distorted[:]

    cam_id2camn = {}
    for cam_id in cam_ids:
        camns = cam_id2camns[cam_id]
        assert len(camns)==1, "can't handle multiple camns per cam_id"
        cam_id2camn[cam_id] = camns[0]

    if 1:
        # narrow search to local region of .h5
        cond = ((first_ufmf_ts <= h5_data[timestamp_name]) &
                (h5_data[timestamp_name] <= last_ufmf_ts))
        narrow_h5_data = h5_data[cond]
        ff = utils.FastFinder(narrow_h5_data['frame'])
        unique_frames = list(np.unique1d(narrow_h5_data['frame']))
        unique_frames.sort()
        unique_frames = np.array( unique_frames )
        if start is not None:
            unique_frames = unique_frames[ unique_frames >= start ]
        if stop is not None:
            unique_frames = unique_frames[ unique_frames <= stop ]

        if max_n_frames is not None:
            unique_frames = unique_frames[:max_n_frames]
        for frame_enum,frame in enumerate(unique_frames):
            narrow_idxs = ff.get_idxs_of_equal(frame)

            # trim data under consideration to just this frame
            this_h5_data = narrow_h5_data[narrow_idxs]
            this_camns = this_h5_data['camn']
            this_tss = this_h5_data[timestamp_name]

            # a couple more checks
            if np.any( this_tss < first_ufmf_ts):
                continue
            if np.any( this_tss >= last_ufmf_ts):
                break

            per_frame_dict = {}
            for ufmf_fname in ufmf_fnames:
                ufmf, cam_id, tss = ufmfs[ufmf_fname]
                camn = cam_id2camn[cam_id]
                this_camn_cond = this_camns == camn
                this_cam_h5_data = this_h5_data[this_camn_cond]
                this_camn_tss = this_cam_h5_data[timestamp_name]
                if not len(this_camn_tss):
                    # no data for this cam_id at this frame
                    continue
                this_camn_ts=np.unique1d(this_camn_tss)
                assert len(this_camn_ts)==1
                this_camn_ts = this_camn_ts[0]

                # optimistic: get next frame. it's probably the one we want
                image,image_ts,more = ufmf.get_next_frame(_return_more=True)
                if this_camn_ts != image_ts:
                    # It was not the frame we wanted. Find it.
                    ufmf_frame_idxs = np.nonzero(tss == this_camn_ts)[0]
                    if (len(ufmf_frame_idxs)==0 and
                        old_camera_timestamp_source):
                        warnings.warn(
                            'low-precision timestamp comparison in '
                            'use due to outdated .ufmf timestamp '
                            'saving.')
                        # 2.5 msec precision required
                        ufmf_frame_idxs = np.nonzero(
                            abs( tss - this_camn_ts ) < 0.0025)[0]
                    assert len(ufmf_frame_idxs)==1
                    ufmf_frame_no = ufmf_frame_idxs[0]
                    image,image_ts,more = ufmf.get_frame(ufmf_frame_no,
                                                         _return_more=True)
                    del ufmf_frame_no, ufmf_frame_idxs
                per_frame_dict[ufmf_fname] = {
                    'image':image,
                    'cam_id':cam_id,
                    'camn':camn,
                    'timestamp':this_cam_h5_data['timestamp'][0],
                    'cam_received_timestamp':
                    this_cam_h5_data['cam_received_timestamp'][0],
                    }
                per_frame_dict[ufmf_fname].update(more)
            per_frame_dict['tracker_data']=this_h5_data
            yield (per_frame_dict,frame)