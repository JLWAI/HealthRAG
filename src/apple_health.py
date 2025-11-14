"""
Apple Health Integration for HealthRAG
Pull health data from Apple Health app on macOS

Data sources:
- Body metrics: weight, height, body fat %
- Activity: steps, active energy, exercise minutes
- Workouts: strength training sessions
- Sleep data
"""

import os
import sqlite3
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
from pathlib import Path
import subprocess


class AppleHealthReader:
    """
    Read data from Apple Health database.

    On macOS, Apple Health stores data in:
    ~/Library/Containers/com.apple.health.healthd/Data/Library/Health/healthdb_secure.hfd

    Note: This requires user permission to access Health data.
    """

    def __init__(self):
        # Find Health database
        self.health_db_path = self._find_health_database()
        self.available = self.health_db_path is not None

    def _find_health_database(self) -> Optional[str]:
        """Locate Apple Health database"""
        possible_paths = [
            os.path.expanduser("~/Library/Containers/com.apple.health.healthd/Data/Library/Health/healthdb_secure.hfd"),
            os.path.expanduser("~/Library/Health/healthdb_secure.hfd"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def is_available(self) -> bool:
        """Check if Apple Health data is accessible"""
        return self.available

    def get_latest_weight(self, days_back: int = 30) -> Optional[Dict]:
        """
        Get most recent weight measurement.

        Returns:
            dict with weight_lbs, date, source
        """
        if not self.available:
            return None

        try:
            # Apple Health stores weight in kg, convert to lbs
            # Query uses healthdb schema
            conn = sqlite3.connect(f"file:{self.health_db_path}?mode=ro", uri=True)
            cursor = conn.cursor()

            # Query for body mass samples
            cursor.execute("""
                SELECT quantity, start_date, source_name
                FROM samples
                WHERE data_type = 3  -- Body Mass
                AND start_date > datetime('now', '-{} days')
                ORDER BY start_date DESC
                LIMIT 1
            """.format(days_back))

            row = cursor.fetchone()
            conn.close()

            if row:
                weight_kg = row[0]
                weight_lbs = weight_kg * 2.20462
                return {
                    'weight_lbs': weight_lbs,
                    'date': row[1],
                    'source': row[2]
                }

        except Exception as e:
            print(f"Error reading Apple Health weight: {e}")

        return None

    def get_height(self) -> Optional[float]:
        """
        Get height from Apple Health.

        Returns:
            Height in inches
        """
        if not self.available:
            return None

        try:
            conn = sqlite3.connect(f"file:{self.health_db_path}?mode=ro", uri=True)
            cursor = conn.cursor()

            # Query for height (stored in meters)
            cursor.execute("""
                SELECT quantity
                FROM samples
                WHERE data_type = 8  -- Height
                ORDER BY start_date DESC
                LIMIT 1
            """)

            row = cursor.fetchone()
            conn.close()

            if row:
                height_meters = row[0]
                height_inches = height_meters * 39.3701
                return height_inches

        except Exception as e:
            print(f"Error reading Apple Health height: {e}")

        return None

    def get_date_of_birth(self) -> Optional[Dict]:
        """
        Get date of birth to calculate age.

        Returns:
            dict with date_of_birth, age
        """
        if not self.available:
            return None

        try:
            conn = sqlite3.connect(f"file:{self.health_db_path}?mode=ro", uri=True)
            cursor = conn.cursor()

            # Query for date of birth
            cursor.execute("""
                SELECT value
                FROM key_value_secure
                WHERE key = 'HKDateOfBirthKey'
            """)

            row = cursor.fetchone()
            conn.close()

            if row:
                dob = datetime.fromisoformat(row[0])
                age = (datetime.now() - dob).days // 365

                return {
                    'date_of_birth': dob.date().isoformat(),
                    'age': age
                }

        except Exception as e:
            print(f"Error reading Apple Health DOB: {e}")

        return None

    def get_biological_sex(self) -> Optional[str]:
        """
        Get biological sex.

        Returns:
            "male" or "female"
        """
        if not self.available:
            return None

        try:
            conn = sqlite3.connect(f"file:{self.health_db_path}?mode=ro", uri=True)
            cursor = conn.cursor()

            # Query for biological sex
            cursor.execute("""
                SELECT value
                FROM key_value_secure
                WHERE key = 'HKBiologicalSexKey'
            """)

            row = cursor.fetchone()
            conn.close()

            if row:
                # Apple Health codes: 1 = Not Set, 2 = Male, 3 = Female, 4 = Other
                sex_code = int(row[0])
                if sex_code == 2:
                    return "male"
                elif sex_code == 3:
                    return "female"

        except Exception as e:
            print(f"Error reading Apple Health sex: {e}")

        return None

    def get_daily_steps(self, days: int = 7) -> List[Dict]:
        """
        Get daily step counts.

        Returns:
            List of dicts with date, steps
        """
        if not self.available:
            return []

        try:
            conn = sqlite3.connect(f"file:{self.health_db_path}?mode=ro", uri=True)
            cursor = conn.cursor()

            # Query for step counts
            cursor.execute("""
                SELECT DATE(start_date) as date, SUM(quantity) as steps
                FROM samples
                WHERE data_type = 7  -- Step Count
                AND start_date > datetime('now', '-{} days')
                GROUP BY DATE(start_date)
                ORDER BY date DESC
            """.format(days))

            rows = cursor.fetchall()
            conn.close()

            return [
                {'date': row[0], 'steps': int(row[1])}
                for row in rows
            ]

        except Exception as e:
            print(f"Error reading Apple Health steps: {e}")

        return []

    def get_profile_data(self) -> Dict:
        """
        Get all relevant profile data from Apple Health.

        Returns:
            Dictionary with weight, height, age, sex, steps
        """
        data = {
            'available': self.available,
            'weight': None,
            'height_inches': None,
            'age': None,
            'sex': None,
            'recent_steps': []
        }

        if not self.available:
            return data

        # Get weight
        weight_data = self.get_latest_weight()
        if weight_data:
            data['weight'] = weight_data

        # Get height
        height = self.get_height()
        if height:
            data['height_inches'] = height

        # Get age
        dob_data = self.get_date_of_birth()
        if dob_data:
            data['age'] = dob_data['age']

        # Get sex
        sex = self.get_biological_sex()
        if sex:
            data['sex'] = sex

        # Get recent steps
        steps = self.get_daily_steps(days=7)
        if steps:
            data['recent_steps'] = steps
            data['avg_daily_steps'] = sum(s['steps'] for s in steps) / len(steps)

        return data


# Fallback: Use Apple HealthKit Export XML
def parse_health_export_xml(xml_path: str) -> Dict:
    """
    Parse Apple Health Export XML file.

    User can export their data:
    Health App → Profile → Export All Health Data

    Args:
        xml_path: Path to export.xml file

    Returns:
        Dictionary with health data
    """
    import xml.etree.ElementTree as ET

    tree = ET.parse(xml_path)
    root = tree.getroot()

    data = {
        'weight_records': [],
        'height_records': [],
        'step_records': []
    }

    for record in root.findall('.//Record'):
        record_type = record.get('type')

        if record_type == 'HKQuantityTypeIdentifierBodyMass':
            # Weight record
            value = float(record.get('value'))  # kg
            date_str = record.get('startDate')
            data['weight_records'].append({
                'weight_lbs': value * 2.20462,
                'date': date_str
            })

        elif record_type == 'HKQuantityTypeIdentifierHeight':
            # Height record
            value = float(record.get('value'))  # meters
            date_str = record.get('startDate')
            data['height_records'].append({
                'height_inches': value * 39.3701,
                'date': date_str
            })

        elif record_type == 'HKQuantityTypeIdentifierStepCount':
            # Steps record
            value = float(record.get('value'))
            date_str = record.get('startDate')[:10]  # Just date, not time
            data['step_records'].append({
                'steps': int(value),
                'date': date_str
            })

    return data


if __name__ == "__main__":
    # Test Apple Health integration
    print("=== Apple Health Integration Test ===\n")

    reader = AppleHealthReader()

    print(f"Apple Health Available: {reader.is_available()}")
    print()

    if reader.is_available():
        print("Fetching profile data...")
        data = reader.get_profile_data()

        print(f"\n📊 Profile Data:")
        if data['weight']:
            print(f"  Weight: {data['weight']['weight_lbs']:.1f} lbs (from {data['weight']['date']})")
        if data['height_inches']:
            feet = int(data['height_inches'] // 12)
            inches = int(data['height_inches'] % 12)
            print(f"  Height: {feet}'{inches}\" ({data['height_inches']:.1f} inches)")
        if data['age']:
            print(f"  Age: {data['age']} years")
        if data['sex']:
            print(f"  Sex: {data['sex']}")
        if data.get('avg_daily_steps'):
            print(f"  Avg Daily Steps (last 7 days): {data['avg_daily_steps']:.0f}")
    else:
        print("⚠️  Apple Health database not found or not accessible")
        print("\nAlternative: Export your data from Health app:")
        print("  1. Open Health app")
        print("  2. Tap your profile picture")
        print("  3. Export All Health Data")
        print("  4. Use parse_health_export_xml() to read the exported XML")
