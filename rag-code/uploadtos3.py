import os
import subprocess

# Define the folder containing extracted PDF text files
output_folder = "pdf_text_output"

# Define your S3 bucket name
s3_bucket = "economics-pdf-files"

def upload_files_to_s3():
    """ Uploads all files in output_folder to the specified S3 bucket using AWS CLI. """
    if not os.path.exists(output_folder):
        print(f"❌ Error: Folder '{output_folder}' does not exist.")
        return

    files = os.listdir(output_folder)
    if not files:
        print(f"❌ No files found in '{output_folder}'.")
        return

    for file in files:
        local_path = os.path.join(output_folder, file)
        s3_path = f"s3://{s3_bucket}/{file}"

        # AWS S3 upload command
        command = f"aws s3 cp {local_path} {s3_path}"
        print(f"🚀 Uploading: {local_path} → {s3_path}")

        # Execute the command
        try:
            subprocess.run(command, shell=True, check=True)
            print(f"✅ Successfully uploaded {file} to S3")
        except subprocess.CalledProcessError as e:
            print(f"❌ Upload failed for {file}: {e}")

# Run the upload function
upload_files_to_s3()
