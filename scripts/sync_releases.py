#!/usr/bin/env python3
"""
GitHub Releases Sync Utility
============================
A zero-dependency automation script to publish and synchronize existing releases
and their local markdown documentation to GitHub.

Author: Antigravity AI
"""

import os
import sys
import json
import urllib.request
import urllib.error
import ssl
import subprocess
import argparse
import getpass

# Hardcoded mapping of the 6 releases
RELEASES = [
    {
        "tag": "v1.0.0",
        "codename": "Insight",
        "commit": "3d67b0ba2a7834d05546af0c879eebb854e8bf28",
        "prerelease": True,
        "type": "Pre-release — internal development milestone"
    },
    {
        "tag": "v1.0.5",
        "codename": "Clarity",
        "commit": "3d67b0ba2a7834d05546af0c879eebb854e8bf28",
        "prerelease": False,
        "type": "Release 1 — first functional build"
    },
    {
        "tag": "v1.1.0",
        "codename": "Momentum",
        "commit": "3d67b0ba2a7834d05546af0c879eebb854e8bf28",
        "prerelease": False,
        "type": "Release 2 — first complete public release"
    },
    {
        "tag": "v1.1.5",
        "codename": "Genesis",
        "commit": "7fe5e78ba63338c8e39a63cf9323a4ff1b07c9e0",
        "prerelease": False,
        "type": "Release 3"
    },
    {
        "tag": "v1.2.0",
        "codename": "Horizon",
        "commit": "84e43205c2b13885497098dc7495893b2f643d48",
        "prerelease": False,
        "type": "Release 4"
    },
    {
        "tag": "v1.2.5",
        "codename": "Apex",
        "commit": "c8e3a2102b908344cd46939267a967bf8918109e",
        "prerelease": False,
        "type": "Release 5 — latest stable"
    }
]

def run_git(args):
    """Run a git command and return stripped stdout."""
    try:
        res = subprocess.run(
            ["git"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except subprocess.SubprocessError:
        return None

def detect_repo():
    """Detect repo owner/name from git remote origin URL."""
    remote_url = run_git(["config", "--get", "remote.origin.url"])
    if not remote_url:
        return "SufiyanAasim/smart-study-planner"
    
    # Handle ssh: git@github.com:owner/repo.git or git@github.com/owner/repo.git
    # Handle https: https://github.com/owner/repo.git or https://github.com/owner/repo
    url = remote_url.replace(".git", "")
    if "github.com" in url:
        if ":" in url:
            parts = url.split("github.com:")[-1]
        else:
            parts = url.split("github.com/")[-1]
        return parts
    return "SufiyanAasim/smart-study-planner"

def get_current_commit():
    """Get the current checked-out commit SHA."""
    return run_git(["rev-parse", "HEAD"])

def make_request(url, method="GET", headers=None, data=None, token=None):
    """Make HTTP request with urllib.request."""
    if headers is None:
        headers = {}
    
    headers["User-Agent"] = "release-sync-script"
    if token:
        headers["Authorization"] = f"token {token}"
    headers["Accept"] = "application/vnd.github.v3+json"
    
    req_data = None
    if data is not None:
        req_data = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"
        
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
    context = ssl._create_unverified_context()
    
    try:
        with urllib.request.urlopen(req, context=context) as response:
            res_data = response.read().decode("utf-8")
            if res_data:
                return response.status, json.loads(res_data)
            return response.status, {}
    except urllib.error.HTTPError as e:
        res_data = e.read().decode("utf-8")
        try:
            err_json = json.loads(res_data)
        except Exception:
            err_json = {"message": res_data}
        return e.code, err_json
    except urllib.error.URLError as e:
        return 0, {"message": str(e.reason)}

def upload_asset(upload_url, file_path, filename, token):
    """Upload asset binary to the release asset endpoint."""
    if "{" in upload_url:
        upload_url = upload_url.split("{")[0]
    
    url = f"{upload_url}?name={filename}"
    
    headers = {
        "User-Agent": "release-sync-script",
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/octet-stream"
    }
    
    try:
        with open(file_path, "rb") as f:
            file_bytes = f.read()
            
        headers["Content-Length"] = str(len(file_bytes))
        
        req = urllib.request.Request(url, data=file_bytes, headers=headers, method="POST")
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context) as response:
            res_data = response.read().decode("utf-8")
            return response.status, json.loads(res_data)
    except Exception as e:
        return 0, {"message": str(e)}

def main():
    parser = argparse.ArgumentParser(description="Synchronize project release notes to GitHub Releases.")
    parser.add_argument("--dry-run", action="store_true", help="Print actions instead of performing requests.")
    parser.add_argument("--token", help="GitHub Personal Access Token (PAT).")
    parser.add_argument("--repo", help="Repository in 'owner/name' format (e.g. SufiyanAasim/smart-study-planner).")
    parser.add_argument("--upload-exe", action="store_true", help="Upload built executable if version matches.")
    args = parser.parse_args()

    repo = args.repo or detect_repo()
    print(f"Targeting Repository: {repo}")

    # Check for token
    token = args.token or os.environ.get("GITHUB_TOKEN")
    if not token and not args.dry_run:
        print("GitHub token not found in env or arguments.")
        token = getpass.getpass("Enter GitHub Personal Access Token (PAT) with repo write permissions: ")
        if not token:
            print("Error: A token is required to perform live sync operations.")
            sys.exit(1)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(project_root, "docs", "releases")
    current_commit = get_current_commit()
    
    print(f"Current checked-out commit: {current_commit}")
    print("Starting Release and Docs synchronization...\n")

    for rel in RELEASES:
        tag = rel["tag"]
        codename = rel["codename"]
        commit = rel["commit"]
        prerelease = rel["prerelease"]
        
        # Read the release doc
        doc_filename = f"{tag}.md"
        doc_path = os.path.join(docs_dir, doc_filename)
        if not os.path.exists(doc_path):
            print(f"[-] Missing release doc for {tag} at: {doc_path} (Skipping...)")
            continue
            
        with open(doc_path, "r", encoding="utf-8") as f:
            release_body = f.read()

        release_name = f"Smart Study Planner {tag} — {codename}"
        print(f"[*] Processing {tag} ({codename})...")

        if args.dry_run:
            print(f"    [Dry-run] Would create/update release: '{release_name}'")
            print(f"    [Dry-run] Target commit: {commit}")
            print(f"    [Dry-run] Prerelease: {prerelease}")
            print(f"    [Dry-run] Body lines: {len(release_body.splitlines())}")
            continue

        # 1. Check if release already exists
        get_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
        status, res = make_request(get_url, method="GET", token=token)
        
        payload = {
            "tag_name": tag,
            "target_commitish": commit,
            "name": release_name,
            "body": release_body,
            "draft": False,
            "prerelease": prerelease
        }

        release_id = None
        upload_url = None

        if status == 200:
            # Update existing release
            release_id = res["id"]
            upload_url = res["upload_url"]
            patch_url = f"https://api.github.com/repos/{repo}/releases/{release_id}"
            print(f"    Release already exists. Updating release {release_id}...")
            up_status, up_res = make_request(patch_url, method="PATCH", data=payload, token=token)
            if up_status in (200, 201):
                print(f"    [+] Successfully updated release {tag} on GitHub.")
            else:
                print(f"    [!] Failed to update release {tag}: {up_res.get('message', 'Unknown error')}")
        elif status == 404:
            # Create new release
            create_url = f"https://api.github.com/repos/{repo}/releases"
            print(f"    Release does not exist. Creating new release on GitHub...")
            cr_status, cr_res = make_request(create_url, method="POST", data=payload, token=token)
            if cr_status in (200, 201):
                release_id = cr_res["id"]
                upload_url = cr_res["upload_url"]
                print(f"    [+] Successfully created release {tag} on GitHub.")
            else:
                print(f"    [!] Failed to create release {tag}: {cr_res.get('message', 'Unknown error')}")
        else:
            print(f"    [!] Error checking release status ({status}): {res.get('message', 'Unknown error')}")

        # 2. Asset Upload (Executable)
        if args.upload_exe and release_id and upload_url:
            # We only upload the executable if the current checked-out commit matches the tag commit,
            # OR if we are on the latest release (v1.2.5) and the executable exists.
            exe_path = os.path.join(project_root, "SmartStudyPlanner.exe")
            
            should_upload = False
            if current_commit == commit:
                should_upload = True
            elif tag == "v1.2.5" and os.path.exists(exe_path):
                # Always upload to v1.2.5 if we have an exe built at root
                should_upload = True
                
            if should_upload and os.path.exists(exe_path):
                filename = f"SmartStudyPlanner-{tag}-windows-x64.exe"
                print(f"    Asset detected: {exe_path}")
                
                # Check if asset already exists in the release
                assets_list_url = f"https://api.github.com/repos/{repo}/releases/{release_id}/assets"
                list_status, assets_list = make_request(assets_list_url, method="GET", token=token)
                
                existing_asset_id = None
                if list_status == 200:
                    for asset in assets_list:
                        if asset["name"] == filename:
                            existing_asset_id = asset["id"]
                            break
                            
                if existing_asset_id:
                    print(f"    Deleting old asset (ID: {existing_asset_id})...")
                    del_url = f"https://api.github.com/repos/{repo}/releases/assets/{existing_asset_id}"
                    make_request(del_url, method="DELETE", token=token)

                print(f"    Uploading asset: {filename}...")
                upload_status, upload_res = upload_asset(upload_url, exe_path, filename, token)
                if upload_status in (200, 201):
                    print(f"    [+] Asset uploaded successfully: {upload_res.get('browser_download_url')}")
                else:
                    print(f"    [!] Failed to upload asset: {upload_res.get('message', 'Unknown error')}")
            else:
                if not os.path.exists(exe_path):
                    print("    [-] Built executable (SmartStudyPlanner.exe) not found at root.")
                else:
                    print(f"    [-] Current commit ({current_commit[:8]}) does not match version commit ({commit[:8]}). Skipping asset upload.")

    print("\nSynchronization flow complete.")

if __name__ == "__main__":
    main()
