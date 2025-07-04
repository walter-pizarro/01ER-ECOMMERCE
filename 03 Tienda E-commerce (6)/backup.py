#!/usr/bin/env python3
"""
Sistema de backup automático para eCommerce Modular
Crea backups de la base de datos con compresión y rotación
"""
import os
import sys
import gzip
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from config.database import get_database_url

class DatabaseBackup:
    """Gestor de backups de base de datos"""
    
    def __init__(self, backup_dir='/home/ubuntu/backups'):
        self.database_url = get_database_url()
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Parsear URL de base de datos
        parsed = urlparse(self.database_url)
        self.host = parsed.hostname
        self.port = parsed.port or 3306
        self.username = parsed.username
        self.password = parsed.password
        self.database = parsed.path.lstrip('/')
        
    def create_backup(self, compress=True):
        """Crea un backup de la base de datos"""
        try:
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            backup_filename = f"ecommerce_backup_{timestamp}.sql"
            backup_path = self.backup_dir / backup_filename
            
            print(f"🔄 Creando backup de la base de datos...")
            print(f"📍 Base de datos: {self.database}")
            print(f"📁 Archivo: {backup_path}")
            
            # Comando mysqldump
            cmd = [
                'mysqldump',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--user={self.username}',
                f'--password={self.password}',
                '--single-transaction',
                '--routines',
                '--triggers',
                '--events',
                '--add-drop-table',
                '--add-locks',
                '--create-options',
                '--disable-keys',
                '--extended-insert',
                '--quick',
                '--lock-tables=false',
                self.database
            ]
            
            # Ejecutar mysqldump
            with open(backup_path, 'w') as f:
                result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                
                if result.returncode != 0:
                    raise Exception(f"Error en mysqldump: {result.stderr}")
            
            # Comprimir si se solicita
            if compress:
                compressed_path = backup_path.with_suffix('.sql.gz')
                
                print(f"🗜️  Comprimiendo backup...")
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Eliminar archivo sin comprimir
                backup_path.unlink()
                backup_path = compressed_path
            
            # Verificar tamaño del archivo
            file_size = backup_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"✅ Backup creado exitosamente!")
            print(f"📊 Tamaño: {file_size_mb:.2f} MB")
            print(f"📁 Ubicación: {backup_path}")
            
            return backup_path
            
        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            raise
    
    def restore_backup(self, backup_path, force=False):
        """Restaura un backup de la base de datos"""
        try:
            backup_path = Path(backup_path)
            
            if not backup_path.exists():
                raise Exception(f"Archivo de backup no encontrado: {backup_path}")
            
            if not force:
                confirm = input(f"⚠️  ¿Estás seguro de que quieres restaurar {backup_path.name}? "
                              f"Esto sobrescribirá la base de datos actual. (yes/no): ")
                if confirm.lower() != 'yes':
                    print("Operación cancelada")
                    return
            
            print(f"🔄 Restaurando backup...")
            print(f"📁 Archivo: {backup_path}")
            
            # Comando mysql
            cmd = [
                'mysql',
                f'--host={self.host}',
                f'--port={self.port}',
                f'--user={self.username}',
                f'--password={self.password}',
                self.database
            ]
            
            # Determinar si el archivo está comprimido
            if backup_path.suffix == '.gz':
                print("🗜️  Descomprimiendo backup...")
                with gzip.open(backup_path, 'rt') as f:
                    result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
            else:
                with open(backup_path, 'r') as f:
                    result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
            
            if result.returncode != 0:
                raise Exception(f"Error en mysql: {result.stderr}")
            
            print(f"✅ Backup restaurado exitosamente!")
            
        except Exception as e:
            print(f"❌ Error restaurando backup: {e}")
            raise
    
    def list_backups(self):
        """Lista todos los backups disponibles"""
        print(f"📋 Backups disponibles en {self.backup_dir}:")
        
        backup_files = list(self.backup_dir.glob("ecommerce_backup_*.sql*"))
        backup_files.sort(reverse=True)  # Más recientes primero
        
        if not backup_files:
            print("   No hay backups disponibles")
            return []
        
        for i, backup_file in enumerate(backup_files, 1):
            file_size = backup_file.stat().st_size / (1024 * 1024)
            modified_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
            
            print(f"   {i:2d}. {backup_file.name}")
            print(f"       Tamaño: {file_size:.2f} MB")
            print(f"       Fecha: {modified_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
        
        return backup_files
    
    def cleanup_old_backups(self, keep_days=30):
        """Elimina backups antiguos"""
        try:
            print(f"🧹 Limpiando backups antiguos (manteniendo {keep_days} días)...")
            
            cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
            backup_files = list(self.backup_dir.glob("ecommerce_backup_*.sql*"))
            
            deleted_count = 0
            for backup_file in backup_files:
                if backup_file.stat().st_mtime < cutoff_time:
                    print(f"   Eliminando: {backup_file.name}")
                    backup_file.unlink()
                    deleted_count += 1
            
            if deleted_count == 0:
                print("   No hay backups antiguos para eliminar")
            else:
                print(f"✅ Eliminados {deleted_count} backups antiguos")
                
        except Exception as e:
            print(f"❌ Error limpiando backups: {e}")
    
    def schedule_backup(self):
        """Crea un cron job para backups automáticos"""
        try:
            script_path = Path(__file__).absolute()
            cron_command = f"0 2 * * * cd {script_path.parent} && python3 {script_path.name} --auto"
            
            print("📅 Para programar backups automáticos, agrega esta línea a tu crontab:")
            print(f"   {cron_command}")
            print()
            print("Ejecuta: crontab -e")
            print("Y agrega la línea anterior para backups diarios a las 2:00 AM")
            
        except Exception as e:
            print(f"❌ Error configurando backup automático: {e}")
    
    def auto_backup(self):
        """Ejecuta backup automático con limpieza"""
        try:
            print("🤖 Ejecutando backup automático...")
            
            # Crear backup
            backup_path = self.create_backup(compress=True)
            
            # Limpiar backups antiguos
            self.cleanup_old_backups(keep_days=30)
            
            print("✅ Backup automático completado")
            
        except Exception as e:
            print(f"❌ Error en backup automático: {e}")
            raise

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de backup eCommerce')
    parser.add_argument('--create', action='store_true', help='Crear nuevo backup')
    parser.add_argument('--restore', type=str, help='Restaurar backup desde archivo')
    parser.add_argument('--list', action='store_true', help='Listar backups disponibles')
    parser.add_argument('--cleanup', type=int, metavar='DAYS', help='Limpiar backups antiguos (días a mantener)')
    parser.add_argument('--schedule', action='store_true', help='Mostrar instrucciones para programar backups')
    parser.add_argument('--auto', action='store_true', help='Ejecutar backup automático')
    parser.add_argument('--no-compress', action='store_true', help='No comprimir backup')
    parser.add_argument('--force', action='store_true', help='Forzar operación sin confirmación')
    parser.add_argument('--backup-dir', type=str, default='/home/ubuntu/backups', help='Directorio de backups')
    
    args = parser.parse_args()
    
    backup_manager = DatabaseBackup(backup_dir=args.backup_dir)
    
    try:
        if args.create:
            backup_manager.create_backup(compress=not args.no_compress)
        elif args.restore:
            backup_manager.restore_backup(args.restore, force=args.force)
        elif args.list:
            backup_manager.list_backups()
        elif args.cleanup:
            backup_manager.cleanup_old_backups(keep_days=args.cleanup)
        elif args.schedule:
            backup_manager.schedule_backup()
        elif args.auto:
            backup_manager.auto_backup()
        else:
            # Comportamiento por defecto: crear backup
            backup_manager.create_backup(compress=not args.no_compress)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

