"""
Module to export ml_module.db content to CSV files

Usage:
    python export_db.py                    # Exports all tables
    python export_db.py --table trained_models   # Export specific table
"""

import sqlite3
import pandas as pd
import os
import argparse
import json
from datetime import datetime
from pathlib import Path


class DatabaseExporter:
    """Export SQLite database content to CSV"""
    
    def __init__(self, db_path: str = "ml_module.db"):
        """
        Initialize exporter
        
        Args:
            db_path: Path to the database file (default: ml_module.db in current directory)
        """
        self.db_path = db_path
        self.export_dir = Path("db_exports")
        self.export_dir.mkdir(exist_ok=True)
        
    def _get_connection(self):
        """Get database connection"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        return sqlite3.connect(self.db_path)
    
    def get_tables(self) -> list:
        """Get list of all tables in database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        return tables
    
    def export_table(self, table_name: str, output_file: str = None) -> str:
        """
        Export a single table to CSV
        
        Args:
            table_name: Name of the table to export
            output_file: Optional custom output filename
            
        Returns:
            Path to the exported CSV file
        """
        conn = self._get_connection()
        
        # Read table into DataFrame
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
        conn.close()
        
        # Generate output filename if not provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.export_dir / f"{table_name}_{timestamp}.csv"
        else:
            output_file = self.export_dir / output_file
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        
        return str(output_file)
    
    def export_all_tables(self) -> dict:
        """
        Export all tables to CSV files
        
        Returns:
            Dictionary mapping table names to export file paths
        """
        tables = self.get_tables()
        results = {}
        
        for table in tables:
            try:
                file_path = self.export_table(table)
                results[table] = {
                    "status": "✅ Success",
                    "file": file_path,
                    "size": os.path.getsize(file_path)
                }
            except Exception as e:
                results[table] = {
                    "status": f"❌ Error: {str(e)}",
                    "file": None,
                    "size": 0
                }
        
        return results
    
    def export_trained_models_with_json(self, output_file: str = None) -> str:
        """
        Export trained_models table with JSON columns expanded
        
        Args:
            output_file: Optional custom output filename
            
        Returns:
            Path to the exported CSV file
        """
        conn = self._get_connection()
        
        # Read table
        df = pd.read_sql_query("SELECT * FROM trained_models", conn)
        conn.close()
        
        # Expand JSON columns
        if 'task_config' in df.columns:
            df['task_config'] = df['task_config'].apply(
                lambda x: json.dumps(json.loads(x)) if isinstance(x, str) else x
            )
        
        if 'evaluation_summary' in df.columns:
            df['evaluation_summary'] = df['evaluation_summary'].apply(
                lambda x: json.dumps(json.loads(x)) if isinstance(x, str) else x
            )
        
        if 'metadata_json' in df.columns:
            df['metadata_json'] = df['metadata_json'].apply(
                lambda x: json.dumps(json.loads(x)) if isinstance(x, str) else x
            )
        
        # Generate output filename if not provided
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.export_dir / f"trained_models_expanded_{timestamp}.csv"
        else:
            output_file = self.export_dir / output_file
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        
        return str(output_file)
    
    def print_summary(self):
        """Print database summary"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        print("=" * 60)
        print(f"📊 Database Summary: {self.db_path}")
        print("=" * 60)
        
        # File info
        file_size = os.path.getsize(self.db_path)
        print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.2f} KB)")
        
        # Tables
        tables = self.get_tables()
        print(f"\n📋 Tables ({len(tables)}):")
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   • {table}: {count} records")
        
        conn.close()
        print("=" * 60)


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Export ml_module.db content to CSV"
    )
    parser.add_argument(
        "--db",
        default="ml_module.db",
        help="Path to database file (default: ml_module.db)"
    )
    parser.add_argument(
        "--table",
        help="Export specific table (if not specified, exports all tables)"
    )
    parser.add_argument(
        "--expand",
        action="store_true",
        help="Expand JSON columns in trained_models table"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show database summary"
    )
    
    args = parser.parse_args()
    
    try:
        exporter = DatabaseExporter(args.db)
        
        # Show summary if requested
        if args.summary:
            exporter.print_summary()
        
        # Export data
        if args.table:
            # Export specific table
            print(f"\n📤 Exporting table '{args.table}'...")
            file_path = exporter.export_table(args.table)
            print(f"✅ Exported to: {file_path}")
        
        elif args.expand:
            # Export with expanded JSON
            print(f"\n📤 Exporting trained_models with expanded JSON...")
            file_path = exporter.export_trained_models_with_json()
            print(f"✅ Exported to: {file_path}")
        
        else:
            # Export all tables
            print(f"\n📤 Exporting all tables...")
            results = exporter.export_all_tables()
            
            for table, result in results.items():
                status = result["status"]
                size = result["size"]
                print(f"  {status}: {table} ({size:,} bytes)")
            
            print(f"\n✅ All files exported to: {exporter.export_dir}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
