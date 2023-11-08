from datetime import datetime
import os

def format_and_sort_skills(skills):
    """
    Format skills with proper capitalization and sort them alphabetically.
    :param skills: A list or set of skills.
    :return: A sorted list of skills with proper capitalization.
    """
    # Assuming the capitalization rule is to capitalize the first letter of each skill
    formatted_skills = [skill.capitalize() for skill in skills]
    # Sort the skills alphabetically
    return sorted(formatted_skills)

def write_skills_to_file(skills, file_path):
    """
    Write skills to a file, sorted and formatted.
    :param skills: A list or set of skills.
    :param file_path: File path to write the skills to.
    """
    with open(file_path, "w") as f:
        for skill in skills:
            f.write(skill + "\n")

def get_timestamped_filename(directory, original_filename):
    """
    Generate a timestamped filename if the original file exists, to avoid overwriting.
    :param original_filename: The original file name.
    :return: A tuple containing the new filename to use and the renamed old file.
    """
    base_filename, file_extension = os.path.splitext(original_filename)
    timestamped_filename = f"{base_filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
    if not os.path.exists(os.path.join(directory, original_filename)):
        return original_filename
    else:
        return timestamped_filename

def rename_file_if_exists(old_filename, new_filename):
    """
    Rename an existing file to a new file name.
    :param old_filename: The current file name.
    :param new_filename: The new file name to rename to.
    """
    if old_filename:
        os.rename(old_filename, new_filename)

def ensure_directory_exists(directory):
    """
    Ensure that a directory exists.
    :param directory: The path to the directory to check.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_output_file_path(directory, filename):
    """
    Construct a file path within the outputs directory, adding a timestamp if the file already exists.
    :param directory: The output directory.
    :param filename: The original file name.
    :return: The full path for the new file to be saved.
    """
    ensure_directory_exists(directory)
    base_filename, file_extension = os.path.splitext(filename)
    timestamped_filename = f"{base_filename}_{datetime.now().strftime('%Y%m%d%H%M%S')}{file_extension}"
    output_filepath = os.path.join(directory, filename)
    timestamped_filepath = os.path.join(directory, timestamped_filename)
    
    return (output_filepath, timestamped_filepath if os.path.exists(output_filepath) else output_filepath)

def rename_and_save_file(src_path, dest_path):
    """
    Rename the source file to the destination path.
    :param src_path: The path to the source file.
    :param dest_path: The path where to save the renamed file.
    """
    if src_path != dest_path:
        os.rename(src_path, dest_path)
