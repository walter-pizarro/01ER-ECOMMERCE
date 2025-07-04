#!/usr/bin/env python3
"""
Script maestro de gestión de base de datos para eCommerce Modular
Facilita todas las operaciones de base de datos desde un solo comando
"""
import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """Imprime banner del sistema"""
    print("="*70)
    print("🗄️  GESTOR DE BASE DE DATOS - eCommerce Modular")
    print("="*70)
    print()

def print_menu():
    """Imprime menú de opciones"""
    print("📋 Opciones disponibles:")
    print()
    print("  🏗️  CONFIGURACIÓN:")
    print("    1. migrate     - Ejecutar migraciones (crear tablas)")
    print("    2. seed        - Poblar con datos de prueba")
    print("    3. reset       - Resetear BD (migrate + seed)")
    print()
    print("  🔧 MANTENIMIENTO:")
    print("    4. backup      - Crear backup de la BD")
    print("    5. restore     - Restaurar backup")
    print("    6. test        - Verificar integridad")
    print()
    print("  📊 INFORMACIÓN:")
    print("    7. status      - Estado de la BD")
    print("    8. list-backups - Listar backups disponibles")
    print("    9. cleanup     - Limpiar backups antiguos")
    print()
    print("  ❓ AYUDA:")
    print("    10. help       - Mostrar ayuda detallada")
    print("    0. exit        - Salir")
    print()

def run_command(script_name, args=None):
    """Ejecuta un script de base de datos"""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ Script no encontrado: {script_path}")
        return False
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando {script_name}: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⚠️  Operación cancelada por el usuario")
        return False

def get_database_status():
    """Obtiene estado de la base de datos"""
    try:
        # Importar aquí para evitar errores si no está configurado
        sys.path.append(str(Path(__file__).parent.parent))
        from config.database import get_database_url
        from sqlalchemy import create_engine, text
        
        database_url = get_database_url()
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Verificar conexión
            conn.execute(text("SELECT 1"))
            
            # Obtener información básica
            result = conn.execute(text(
                "SELECT COUNT(*) as table_count FROM INFORMATION_SCHEMA.TABLES "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'"
            ))
            table_count = result.scalar()
            
            # Obtener tamaño de BD
            result = conn.execute(text(
                "SELECT ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS size_mb "
                "FROM information_schema.tables WHERE table_schema = DATABASE()"
            ))
            size_mb = result.scalar() or 0
            
            print("✅ Conexión a base de datos exitosa")
            print(f"📊 Tablas: {table_count}")
            print(f"💾 Tamaño: {size_mb} MB")
            
            # Verificar algunas tablas importantes
            important_tables = ['users', 'products', 'orders', 'categories']
            existing_tables = []
            
            for table in important_tables:
                result = conn.execute(text(
                    f"SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES "
                    f"WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table}'"
                ))
                if result.scalar() > 0:
                    existing_tables.append(table)
            
            if existing_tables:
                print(f"📋 Tablas principales: {', '.join(existing_tables)}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False

def show_help():
    """Muestra ayuda detallada"""
    print("📖 AYUDA DETALLADA")
    print("="*50)
    print()
    print("🏗️  CONFIGURACIÓN INICIAL:")
    print("  1. Ejecuta 'migrate' para crear todas las tablas")
    print("  2. Ejecuta 'seed' para poblar con datos de prueba")
    print("  3. O usa 'reset' para hacer ambos pasos")
    print()
    print("🔧 MANTENIMIENTO REGULAR:")
    print("  - Usa 'backup' antes de cambios importantes")
    print("  - Ejecuta 'test' periódicamente para verificar integridad")
    print("  - Usa 'cleanup' para mantener espacio en disco")
    print()
    print("📁 ARCHIVOS IMPORTANTES:")
    print("  - migrate.py: Crea estructura de BD")
    print("  - seed.py: Datos de prueba")
    print("  - backup.py: Gestión de backups")
    print("  - test_integrity.py: Verificación de integridad")
    print()
    print("🔗 COMANDOS DIRECTOS:")
    print("  También puedes ejecutar los scripts directamente:")
    print("  ./migrate.py --help")
    print("  ./seed.py --help")
    print("  ./backup.py --help")
    print("  ./test_integrity.py --help")
    print()

def interactive_mode():
    """Modo interactivo"""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input("Selecciona una opción (0-10): ").strip()
            print()
            
            if choice == '0' or choice.lower() == 'exit':
                print("👋 ¡Hasta luego!")
                break
                
            elif choice == '1' or choice.lower() == 'migrate':
                print("🏗️  Ejecutando migraciones...")
                run_command('migrate.py')
                
            elif choice == '2' or choice.lower() == 'seed':
                print("🌱 Poblando con datos de prueba...")
                run_command('seed.py')
                
            elif choice == '3' or choice.lower() == 'reset':
                print("🔄 Reseteando base de datos...")
                confirm = input("⚠️  ¿Estás seguro? Esto eliminará todos los datos (yes/no): ")
                if confirm.lower() == 'yes':
                    if run_command('migrate.py', ['--rollback', '--force']):
                        if run_command('migrate.py'):
                            run_command('seed.py')
                else:
                    print("Operación cancelada")
                    
            elif choice == '4' or choice.lower() == 'backup':
                print("💾 Creando backup...")
                run_command('backup.py', ['--create'])
                
            elif choice == '5' or choice.lower() == 'restore':
                print("📋 Listando backups disponibles...")
                if run_command('backup.py', ['--list']):
                    backup_file = input("Ingresa el nombre del archivo de backup: ").strip()
                    if backup_file:
                        run_command('backup.py', ['--restore', backup_file])
                
            elif choice == '6' or choice.lower() == 'test':
                print("🧪 Verificando integridad...")
                run_command('test_integrity.py')
                
            elif choice == '7' or choice.lower() == 'status':
                print("📊 Verificando estado de la base de datos...")
                get_database_status()
                
            elif choice == '8' or choice.lower() == 'list-backups':
                print("📋 Listando backups...")
                run_command('backup.py', ['--list'])
                
            elif choice == '9' or choice.lower() == 'cleanup':
                days = input("¿Cuántos días de backups mantener? (default: 30): ").strip()
                days = days if days.isdigit() else '30'
                run_command('backup.py', ['--cleanup', days])
                
            elif choice == '10' or choice.lower() == 'help':
                show_help()
                
            else:
                print("❌ Opción inválida. Intenta de nuevo.")
            
            print()
            input("Presiona Enter para continuar...")
            print("\n" + "="*70 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except EOFError:
            print("\n\n👋 ¡Hasta luego!")
            break

def command_mode(args):
    """Modo de comando directo"""
    if not args:
        print("❌ No se especificó comando")
        print("Usa: ./db.py help para ver opciones")
        return
    
    command = args[0].lower()
    
    if command == 'migrate':
        run_command('migrate.py', args[1:])
    elif command == 'seed':
        run_command('seed.py', args[1:])
    elif command == 'backup':
        run_command('backup.py', args[1:])
    elif command == 'restore':
        if len(args) > 1:
            run_command('backup.py', ['--restore'] + args[1:])
        else:
            print("❌ Especifica el archivo de backup")
    elif command == 'test':
        run_command('test_integrity.py', args[1:])
    elif command == 'status':
        get_database_status()
    elif command == 'help':
        show_help()
    elif command == 'reset':
        print("🔄 Reseteando base de datos...")
        if '--force' in args or input("⚠️  ¿Estás seguro? (yes/no): ").lower() == 'yes':
            if run_command('migrate.py', ['--rollback', '--force']):
                if run_command('migrate.py'):
                    run_command('seed.py')
    else:
        print(f"❌ Comando desconocido: {command}")
        print("Usa: ./db.py help para ver opciones")

def main():
    """Función principal"""
    # Cambiar al directorio del script
    os.chdir(Path(__file__).parent)
    
    if len(sys.argv) > 1:
        # Modo comando
        command_mode(sys.argv[1:])
    else:
        # Modo interactivo
        interactive_mode()

if __name__ == "__main__":
    main()

