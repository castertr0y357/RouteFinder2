#!/usr/bin/env python
import os
import sys
import argparse
import datetime
import gzip
import shutil
import subprocess

def main() -> None:
    parser = argparse.ArgumentParser(description="Backup or restore the RouteFinder2 database.")
    parser.add_argument("--restore", type=str, help="Path to the backup file to restore.")
    args = parser.parse_args()

    # Bootstrap Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RouteFinder.settings')
    try:
        import django
        django.setup()
    except Exception as e:
        print(f"[Backup] - Error - Failed to bootstrap Django settings: {e}")
        sys.exit(1)

    from django.conf import settings
    db_config = settings.DATABASES['default']
    engine = db_config['ENGINE']

    if args.restore:
        # Restore logic
        restore_path = args.restore
        if not os.path.exists(restore_path):
            print(f"[Backup] - Error - Restore file does not exist: {restore_path}")
            sys.exit(1)
        
        if 'sqlite3' in engine:
            db_file = db_config['NAME']
            print(f"[Backup] - Restore - Restoring SQLite database to {db_file}...")
            try:
                if restore_path.endswith('.gz'):
                    with gzip.open(restore_path, 'rb') as f_in:
                        with open(db_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                else:
                    shutil.copyfile(restore_path, db_file)
                print("[Backup] - Restore - SQLite database restored successfully.")
            except Exception as e:
                print(f"[Backup] - Error - SQLite restore failed: {e}")
                sys.exit(1)
        elif 'postgresql' in engine:
            db_name = db_config['NAME']
            db_user = db_config.get('USER', '')
            db_password = db_config.get('PASSWORD', '')
            db_host = db_config.get('HOST', '')
            db_port = db_config.get('PORT', '')
            
            print(f"[Backup] - Restore - Restoring PostgreSQL database {db_name}...")
            env = os.environ.copy()
            if db_password:
                env['PGPASSWORD'] = db_password
                
            cmd = ['psql']
            if db_host: cmd.extend(['-h', db_host])
            if db_port: cmd.extend(['-p', str(db_port)])
            if db_user: cmd.extend(['-U', db_user])
            cmd.append(db_name)
            
            try:
                if restore_path.endswith('.gz'):
                    with gzip.open(restore_path, 'rb') as f_in:
                        p = subprocess.Popen(cmd, stdin=subprocess.PIPE, env=env)
                        # Type assertion helper for mypy/typing
                        assert p.stdin is not None
                        shutil.copyfileobj(f_in, p.stdin)
                        p.stdin.close()
                        p.wait()
                        if p.returncode != 0:
                            raise Exception(f"psql returned non-zero code {p.returncode}")
                else:
                    with open(restore_path, 'r') as f_in:
                        subprocess.run(cmd, stdin=f_in, check=True, env=env)
                print("[Backup] - Restore - PostgreSQL database restored successfully.")
            except Exception as e:
                print(f"[Backup] - Error - PostgreSQL restore failed: {e}")
                sys.exit(1)
        else:
            print(f"[Backup] - Error - Unsupported database engine: {engine}")
            sys.exit(1)
    else:
        # Backup logic
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if 'sqlite3' in engine:
            db_file = db_config['NAME']
            backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sqlite3.gz")
            print(f"[Backup] - Dump - Backing up SQLite database {db_file} to {backup_file}...")
            try:
                with open(db_file, 'rb') as f_in:
                    with gzip.open(backup_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"[Backup] - Dump - SQLite backup completed successfully: {backup_file}")
            except Exception as e:
                print(f"[Backup] - Error - SQLite backup failed: {e}")
                sys.exit(1)
        elif 'postgresql' in engine:
            db_name = db_config['NAME']
            db_user = db_config.get('USER', '')
            db_password = db_config.get('PASSWORD', '')
            db_host = db_config.get('HOST', '')
            db_port = db_config.get('PORT', '')
            backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql.gz")
            
            print(f"[Backup] - Dump - Backing up PostgreSQL database {db_name} to {backup_file}...")
            env = os.environ.copy()
            if db_password:
                env['PGPASSWORD'] = db_password
                
            cmd = ['pg_dump']
            if db_host: cmd.extend(['-h', db_host])
            if db_port: cmd.extend(['-p', str(db_port)])
            if db_user: cmd.extend(['-U', db_user])
            cmd.append(db_name)
            
            try:
                with gzip.open(backup_file, 'wb') as f_out:
                    subprocess.run(cmd, stdout=f_out, check=True, env=env)
                print(f"[Backup] - Dump - PostgreSQL backup completed successfully: {backup_file}")
            except Exception as e:
                print(f"[Backup] - Error - PostgreSQL backup failed: {e}")
                sys.exit(1)
        else:
            print(f"[Backup] - Error - Unsupported database engine: {engine}")
            sys.exit(1)

if __name__ == '__main__':
    main()
