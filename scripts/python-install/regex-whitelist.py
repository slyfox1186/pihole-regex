        # If this mount's destination is /etc/pihole
        if json_dict['Destination'] == r'/etc/pihole':
            # Use the source path as our target
            docker_mnt_src = json_dict['Source']
            break

    # If we successfully found the mount
    if docker_mnt_src:
        print('[i] Running in docker installation mode.')
        # Prepend restart commands
        cmd_restart[0:0] = ['docker', 'exec', '-i', 'pihole']
else:
    print('[i] Running in physical installation mode ')

# Set paths
path_pihole = docker_mnt_src if docker_mnt_src else r'/etc/pihole'
path_legacy_regex = os.path.join(path_pihole, 'regex.list')
path_legacy_slyfox1186_regex = os.path.join(path_pihole, 'slyfox1186-regex.list')
path_pihole_db = os.path.join(path_pihole, 'gravity.db')

# Check that pi-hole path exists
if os.path.exists(path_pihole):
    print('[i] Pi-hole path exists.')
else:
    print(f'[e] {path_pihole} was not found.')
    exit(1)

# Check for write access to /etc/pihole
if os.access(path_pihole, os.X_OK | os.W_OK):
    print(f'[i] Write access to {path_pihole} verified.')
else:
    print(f'[e] Write access is not available for {path_pihole}. Please run as root or other privileged user.')
    exit(1)

# Determine whether we are using database or not
if os.path.isfile(path_pihole_db) and os.path.getsize(path_pihole_db) > 0:
    db_exists = True
    print('[i] database detected.')
else:
    print('[i] Legacy regex.list detected.')

# Fetch the remote regex strings
str_regexps_remote = fetch_whitelist_url(url_regexps_remote)

# If regex strings were fetched, remove any comments and add to set
if str_regexps_remote:
    regexps_remote.update(x for x in map(str.strip, str_regexps_remote.splitlines()) if x and x[:1] != '#')
    print(f'[i] {len(regexps_remote)} regex strings collected from {url_regexps_remote}.')
else:
    print('[i] No remote regex strings were found.')
    exit(1)

if db_exists:
    # Create a database connection
    print(f'[i] Connecting to {path_pihole_db}')
