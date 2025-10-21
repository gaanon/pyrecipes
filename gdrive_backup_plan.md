# Plan: Backing Up `pyrecipes` to Google Drive

This document outlines the plan to automatically back up the `pyrecipes` application data to Google Drive for added redundancy.

## 1. `rclone` Setup on Raspberry Pi

`rclone` is a command-line program to manage files on cloud storage. We will use it to copy the backups to Google Drive.

### Installation

1.  **Install `rclone`:**
    ```bash
    sudo -v ; curl https://rclone.org/install.sh | sudo bash
    ```

### Configuration

1.  **Start the `rclone` configuration process:**
    ```bash
    rclone config
    ```

2.  **Create a new remote:**
    - When prompted, select `n` for a new remote.
    - Enter a name for the remote, for example, `gdrive`.
    - From the list of storage options, select the number corresponding to **Google Drive**.
    - For `client_id` and `client_secret`, you can leave them blank and press Enter.
    - For `scope`, choose option `1` for full access to all files.
    - For `root_folder_id`, leave it blank to use the root of your Google Drive.
    - For `service_account_file`, leave it blank.
    - When asked about editing advanced config, choose `n` (No).
    - `rclone` will then ask if you want to use auto-config. Since the Raspberry Pi is likely headless, choose `n` (No).
    - `rclone` will display a command to run on a machine with a web browser to get a verification code. It will look something like this:
      ```
      rclone authorize "drive" "your_token_here"
      ```
    - Copy this command and run it on your local machine (not the Raspberry Pi).
    - Your web browser will open, and you'll be asked to log in to your Google account and grant `rclone` permission.
    - After granting permission, you will get a verification code. Copy this code.
    - Paste the verification code back into the `rclone config` session on your Raspberry Pi.
    - `rclone` will ask if this is a Team Drive. Unless you are using a Google Workspace account and want to back up to a shared drive, choose `n`.
    - Review the configuration and if everything looks correct, choose `y` to save.
    - Finally, type `q` to quit the configuration.

3.  **Verify the setup:**
    You can list the contents of your Google Drive root by running:
    ```bash
    rclone ls gdrive:
    ```

## 2. Python Script Modifications

I will modify the `backup_app.py` script to include a function that uploads the backup to Google Drive.

### New Function: `upload_to_gdrive`

I will add the following function to `backup_app.py`:

```python
def upload_to_gdrive(source_path, remote_path):
    """Uploads a directory to Google Drive using rclone."""
    print("\nUploading backup to Google Drive...")
    if not remote_path:
        print("Warning: Google Drive remote path not configured. Skipping upload.")
        return

    command = ["rclone", "copy", source_path, remote_path, "--create-empty-src-dirs"]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        print(f"Successfully uploaded backup to {remote_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error uploading to Google Drive: {e.stderr}")
        sys.exit(1)

```

### Modifications to `main` and `argparse`

I will update the `main` function and the argument parser to handle the Google Drive upload.

-   **Argument Parser:** A new `--gdrive-remote` argument will be added to specify the destination path on Google Drive.

    ```python
    parser.add_argument(
        "--gdrive-remote",
        type=str,
        default="",
        help="The rclone remote path for Google Drive backup (e.g., gdrive:backups)."
    )
    ```

-   **`main` function:** The `upload_to_gdrive` function will be called after the local backup is successfully created.

    ```python
    def main(days_to_keep, gdrive_remote):
        # ... (existing backup code) ...
        try:
            # ... (existing backup logic) ...
            print("\nBackup process completed successfully!")
            print(f"All backup files are located in: {backup_dir}")

            if gdrive_remote:
                upload_to_gdrive(backup_dir, gdrive_remote)

            if days_to_keep:
                rotate_backups(backup_base_dir, days_to_keep)

        # ... (exception handling) ...

    if __name__ == "__main__":
        # ... (argparse setup) ...
        args = parser.parse_args()
        main(args.days_to_keep, args.gdrive_remote)
    ```

This plan ensures that your backups are securely and automatically copied to your Google Drive.