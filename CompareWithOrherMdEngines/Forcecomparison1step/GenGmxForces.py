import os
import subprocess
import csv

def get_subdirectories(base_dir):
    """Retrieve a list of subdirectories within the specified base directory."""
    return [os.path.join(base_dir, d) for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

def clean_backup_files(directory):
    """Remove unwanted backup files from the directory."""
    for file in os.listdir(directory):
        if file.startswith("#") and file.endswith("#"):
            os.remove(os.path.join(directory, file))


def run_gromacs_simulation(directory):
    """Run a single GROMACS simulation step in the specified directory."""
    grompp_cmd = [
        "gmx", "grompp",
        "-f", "../sim.mdp",
        "-c", "conf.gro",
        "-p", "topol.top",
        "-o", "md.tpr"
    ]
    subprocess.run(grompp_cmd, cwd=directory, check=True)

    mdrun_cmd = ["gmx", "mdrun", "-s", "md.tpr", "-rerun", "conf.gro"]
    subprocess.run(mdrun_cmd, cwd=directory, check=True)

def extract_forces(directory):
    """Extract forces from the simulation and write them to forces.csv."""
    forces_file = os.path.join(directory, "forces.xvg")
    extract_cmd = [
    "gmx", "traj", "-s", "md.tpr", "-f", "traj.trr", "-of", "forces.xvg"
    ]
    subprocess.run(extract_cmd, cwd=directory, check=True, text=True, input="0")


    # Process the resulting forces from forces.xvg
    with open(forces_file, 'r') as forces, open(os.path.join(directory, "forces.csv"), 'w', newline='') as csv_out:
        csv_writer = csv.writer(csv_out)
        #csv_writer.writerow(["Atom", "Fx (kJ/mol/nm)", "Fy (kJ/mol/nm)", "Fz (kJ/mol/nm)"])
        for line in forces:
            if not line.startswith("#") and not line.startswith("@"):
                parts = line.split()
                time = parts[0]  # First column is time, can be ignored

                # Extract force data for all atoms
                forces_data = parts[1:]
                num_atoms = len(forces_data) // 3

                for atom_index in range(1, num_atoms + 1):
                    fx, fy, fz = forces_data[(atom_index - 1) * 3:atom_index * 3]
                    csv_writer.writerow([fx, fy, fz])

def process_directories(base_dir):
    """Process all subdirectories in the base directory."""
    subdirectories = get_subdirectories(base_dir)
    for sub_dir in subdirectories:
        try:
            run_gromacs_simulation(sub_dir)
            extract_forces(sub_dir)
            clean_backup_files(sub_dir)
        except subprocess.CalledProcessError as e:
            print(f"Error processing directory {sub_dir}: {e}")

if __name__ == "__main__":
    base_directory = "./"  # Replace with your actual base directory
    process_directories(base_directory)
