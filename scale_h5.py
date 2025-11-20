import h5py
import numpy as np
from scipy.interpolate import interp1d
import os
import argparse

def scale_h5(input_path, scale_y):
    # output file
    base, ext = os.path.splitext(input_path)
    output_path = f"{base}_scale{scale_y}{ext}"

    print(f"Loading: {input_path}")
    with h5py.File(input_path, "r") as f:
        odor_group = f["odor"]
        frame_keys = sorted(odor_group.keys(), key=lambda x: int(x))

        # sample frame
        sample = np.array(odor_group[frame_keys[0]])
        ny, nx = sample.shape

        ny_new = int(ny * scale_y)
        print(f"Original Y: {ny}, New Y: {ny_new}")

        # prepare coordinate arrays for interpolation
        y_old = np.arange(ny)
        y_new = np.linspace(0, ny - 1, ny_new)

        # allocate output array in memory
        total_frames = len(frame_keys)
        scaled = np.zeros((total_frames, ny_new, nx), dtype=sample.dtype)

        print("Processing frames...")
        for i, k in enumerate(frame_keys):
            frame = np.array(odor_group[k])
            f_interp = interp1d(y_old, frame, axis=0, kind='linear')
            scaled[i] = f_interp(y_new)

    # write new h5
    print(f"Saving scaled file to: {output_path}")
    with h5py.File(output_path, "w") as f_out:
        g = f_out.create_group("odor")
        for i, frame in enumerate(scaled):
            # g.create_dataset(str(i), data=frame, compression="gzip")
            g.create_dataset(str(i), data=frame, compression="gzip")

    print("Done.")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scale odor frames along Y in an H5 file.")
    parser.add_argument("input_file", type=str, help="path to the input .h5 file")
    parser.add_argument("--scale_y", type=float, default=1.0, help="scale factor for Y axis")

    args = parser.parse_args()
    scale_h5(args.input_file, args.scale_y)

