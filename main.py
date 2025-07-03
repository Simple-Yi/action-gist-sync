import os
import shutil
import git


def parse_mapping_lines(lines_iterator):
    """
    核心解析逻辑，处理一个包含多行映射规则的迭代器
    """
    mapping = {}
    skipped_files = []

    for i, line in enumerate(lines_iterator, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        parts = [p.strip() for p in line.split(':', 1)]
        source_path = parts[0]

        if not os.path.isfile(source_path):
            print(f"Warning: Source file '{source_path}' on line {i} not found. Skipping.")
            skipped_files.append(source_path)
            continue
        try:
            with open(source_path, 'r', encoding='utf-8') as sf:
                sf.read(1024)
        except (UnicodeDecodeError, IOError):
            print(f"Warning: Source file '{source_path}' on line {i} is not a readable text file. Skipping.")
            skipped_files.append(source_path)
            continue

        if len(parts) == 2 and parts[1]: # 确保冒号后面有内容
            gist_filename = parts[1]
        else:
            gist_filename = os.path.basename(source_path)
        
        mapping[source_path] = gist_filename

    if skipped_files:
        print(f"Skipped a total of {len(skipped_files)} files from mapping list.")
        
    return mapping


if __name__ == '__main__':
    # 1. 获取输入
    gist_id = os.environ['INPUT_GIST_ID']
    gist_token = os.environ['INPUT_GIST_TOKEN']
    
    # 优先使用 mapping_content，否则回退到 mapping_file
    mapping_content = os.environ.get('INPUT_MAPPING_CONTENT')
    mapping_file_path = os.environ.get('INPUT_MAPPING_FILE')

    # 2. 解析清单并构建文件映射
    source_to_gist_map = {}
    
    if mapping_content:
        print("Parsing mapping from 'mapping_content' input.")
        # 将多行字符串分割成行列表
        lines = mapping_content.splitlines()
        source_to_gist_map = parse_mapping_lines(lines)
    elif mapping_file_path:
        print(f"Parsing mapping from file: '{mapping_file_path}'")
        try:
            with open(mapping_file_path, 'r', encoding='utf-8') as f:
                source_to_gist_map = parse_mapping_lines(f)
        except FileNotFoundError:
                raise ValueError(f"Mapping file not found at: {mapping_file_path}")
    else:
        raise ValueError("No mapping provided. Please set 'mapping_file' or 'mapping_content' input.")

    if not source_to_gist_map:
        print("Mapping is empty or all specified files were skipped. Nothing to sync.")
        exit(0)

    print(f"Found {len(source_to_gist_map)} valid files to sync.")

    # 3. 克隆 Gist 仓库
    gist_repo_url = f'https://{gist_token}@gist.github.com/{gist_id}.git'
    local_repo_path = f'gist-clone/{gist_id}'

    if os.path.exists(local_repo_path):
        shutil.rmtree(local_repo_path)
    
    repo = git.Repo.clone_from(gist_repo_url, local_repo_path, depth=1)

    # 4. 同步文件
    target_filenames_in_gist = set(source_to_gist_map.values())
    
    removed_count = 0
    for gist_file in os.listdir(local_repo_path):
        if gist_file == '.git': continue
        if gist_file not in target_filenames_in_gist:
            os.remove(os.path.join(local_repo_path, gist_file))
            removed_count += 1
            print(f"  - Removing stale file from Gist: {gist_file}")
    if removed_count > 0: print(f"Removed {removed_count} stale files from Gist.")

    print("Syncing files to Gist...")
    for source, dest in source_to_gist_map.items():
        print(f"  - Syncing '{source}' -> '{dest}'")
        shutil.copy(source, os.path.join(local_repo_path, dest))

    # 5. 提交并推送变更
    if not repo.is_dirty(untracked_files=True):
        print('No changes detected in Gist repo. Nothing to commit.')
        exit(0)
    
    actor = os.environ['GITHUB_ACTOR']
    with repo.config_writer() as git_config:
        git_config.set_value('user', 'name', actor)
        git_config.set_value('user', 'email', f'{actor}@users.noreply.github.com')

    repo.git.add(A=True)
    commit_message = f'Sync from repo by {actor}, ref: {os.environ["GITHUB_REF"]}'
    repo.index.commit(commit_message)
    repo.remotes.origin.push()

    print('Successfully pushed changes to Gist.')
    