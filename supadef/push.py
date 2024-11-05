import os
import requests
from .network import GET, GET_TEXT, POST
from .util import run_step, serialize_exception, FailMode
from .filesystem import create_tempdir, zip_directory, get_non_ignored_files, copy_dir


def zip_directory_in_isolated_tempdir_v2(path_to_code: str) -> str:
    # create an isolated directory to build the package
    work_dir = create_tempdir('supadef_packages')

    def read_gitignore():
        gitignore_path = os.path.join(path_to_code, '.gitignore')

        # Check if .gitignore file exists
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as file:
                content = file.read()
            return content
        return ''
    # pull down the default .sd_ignore
    default_sd_ignore = GET_TEXT('/defaults/.sd_ignore')

    # read in the user's .gitignore
    user_git_ignore = read_gitignore()

    copy_dir(path_to_code, work_dir, default_sd_ignore + '\n' + user_git_ignore)

    # wire up the full path to the package.zip file
    zip_filename = "package.zip"
    path_to_package_zip = os.path.join(work_dir, zip_filename)
    # zip up the code in the working dir, which has the client code. place output in that dir
    zip_directory(work_dir, path_to_package_zip)
    return path_to_package_zip


def push_project(project_name: str, path_to_code: str, debug: bool = False):
    """Push code to a project"""

    def __log_debug(msg, sp=None):
        """
        log a message when debug mode is enabled
        """
        if debug:
            if sp:
                sp.write(msg)
            else:
                print(msg)

    def step1_zip(sp):
        __log_debug(f'path_to_code: {path_to_code}', sp)
        path_to_zip = zip_directory_in_isolated_tempdir_v2(
            path_to_code)
        __log_debug(f'path_to_zip: {path_to_zip}', sp)
        filename = os.path.basename(path_to_zip)
        return path_to_zip, filename

    path_to_zip, filename = run_step('Package code as .zip', step1_zip)

    def step2_get_upload_url(sp):
        r = GET('/cli/get_upload_zip_presigned_url',
                params={'project_name': project_name, 'file_name': filename})
        __log_debug(f"GET('/cli/get_upload_zip_presigned_url') -> {r}", sp)
        if not 'url' in r:
            raise ValueError('Could not get upload URL - missing url')
        if not 'fields' in r:
            raise ValueError('Could not get upload URL - missing fields')
        return r

    presigned_post_data = run_step('Get upload URL', step2_get_upload_url)

    def step3_upload_zip(sp):
        def upload_file_with_redirect_handling(url, fields, file_path):
            max_retries = 3  # Number of retries
            for attempt in range(max_retries):
                try:
                    # Open the file to upload
                    with open(file_path, 'rb') as file:
                        __log_debug(f'[start] POST: {url}', sp)
                        response = requests.post(
                            url,
                            data=fields,
                            files={'file': (fields['key'], file)},
                            allow_redirects=False,  # Disable automatic redirect handling
                        )
                        __log_debug(f'[response] POST: {url} | {response}', sp)

                    # Check if a redirect is needed
                    if response.status_code in [301, 302]:
                        redirect_url = response.headers.get('Location')
                        if redirect_url:
                            __log_debug(f"Redirecting to: {redirect_url}", sp)
                            # Retry the upload at the new endpoint
                            url = redirect_url
                            continue
                        else:
                            raise ValueError(
                                'Redirect location not provided in response')
                    else:
                        # If no redirect is needed or request is successful, break the loop
                        response.raise_for_status()
                        return response

                except requests.RequestException as e:
                    __log_debug(f"Error during upload: {str(e)}", sp)
                    if attempt < max_retries - 1:
                        __log_debug("Retrying...", sp)
                    else:
                        raise  # Re-raise the exception if max retries exceeded

        return upload_file_with_redirect_handling(
            presigned_post_data['url'], presigned_post_data['fields'], path_to_zip)

    try:
        upload_response = run_step(
            f'Upload package to project:{project_name}', step3_upload_zip, fail_mode=FailMode.THROW_ERROR)

        json = POST('/cli/finish_zip_upload', {
            'name': project_name,
            'status': 'success'
        })
    except Exception as e:
        json = POST('/cli/finish_zip_upload', {
            'name': project_name,
            'status': 'error',
            'error': serialize_exception(e)
        })
