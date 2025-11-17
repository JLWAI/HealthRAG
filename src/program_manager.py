"""
Program Manager for HealthRAG
Manage multiple training programs with history and versioning

Features:
- Save programs with timestamps (don't overwrite)
- Track active program
- View program history
- Archive completed programs
"""

import os
import json
from datetime import datetime, date
from typing import List, Dict, Optional
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ProgramMetadata:
    """Metadata for a saved program"""
    program_id: str
    template_name: str
    start_date: str
    created_at: str
    is_active: bool
    weeks_completed: int = 0
    total_weeks: int = 6


class ProgramManager:
    """
    Manage training program history and versioning.

    Programs are saved to data/programs/ with timestamps
    Active program is tracked in data/active_program.json
    """

    def __init__(self, programs_dir: str = "data/programs"):
        self.programs_dir = Path(programs_dir)
        self.programs_dir.mkdir(parents=True, exist_ok=True)
        self.active_program_file = Path("data/active_program.json")

    def save_program(self, program_data: Dict, set_as_active: bool = True) -> str:
        """
        Save a training program with timestamp.

        Args:
            program_data: Program data dictionary
            set_as_active: Whether to set this as the active program

        Returns:
            program_id: Unique ID for this program
        """
        # Generate program ID from timestamp
        program_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Add metadata
        program_data['program_id'] = program_id
        program_data['created_at'] = datetime.now().isoformat()
        program_data['is_active'] = set_as_active
        program_data['weeks_completed'] = 0

        # Save program file
        program_file = self.programs_dir / f"program_{program_id}.json"
        with open(program_file, 'w') as f:
            json.dump(program_data, f, indent=2)

        # Set as active if requested
        if set_as_active:
            self.set_active_program(program_id)

        return program_id

    def get_program(self, program_id: str) -> Optional[Dict]:
        """Get a specific program by ID"""
        program_file = self.programs_dir / f"program_{program_id}.json"

        if not program_file.exists():
            return None

        with open(program_file, 'r') as f:
            return json.load(f)

    def get_active_program(self) -> Optional[Dict]:
        """Get the currently active program"""
        if not self.active_program_file.exists():
            # Try to find most recent program
            programs = self.list_programs()
            if programs:
                return self.get_program(programs[0]['program_id'])
            return None

        with open(self.active_program_file, 'r') as f:
            active_data = json.load(f)
            program_id = active_data.get('program_id')
            if program_id:
                return self.get_program(program_id)

        return None

    def set_active_program(self, program_id: str) -> bool:
        """Set a program as active"""
        # Verify program exists
        if not self.get_program(program_id):
            return False

        # Update active program file
        with open(self.active_program_file, 'w') as f:
            json.dump({
                'program_id': program_id,
                'set_at': datetime.now().isoformat()
            }, f, indent=2)

        return True

    def list_programs(self, limit: int = 10) -> List[ProgramMetadata]:
        """
        List all saved programs, most recent first.

        Args:
            limit: Maximum number of programs to return

        Returns:
            List of ProgramMetadata objects
        """
        programs = []

        # Get all program files
        program_files = sorted(
            self.programs_dir.glob("program_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        active_program_id = None
        if self.active_program_file.exists():
            with open(self.active_program_file, 'r') as f:
                active_data = json.load(f)
                active_program_id = active_data.get('program_id')

        for program_file in program_files[:limit]:
            try:
                with open(program_file, 'r') as f:
                    data = json.load(f)

                    programs.append(ProgramMetadata(
                        program_id=data.get('program_id', program_file.stem.replace('program_', '')),
                        template_name=data.get('template_name', 'Unknown'),
                        start_date=data.get('start_date', ''),
                        created_at=data.get('created_at', ''),
                        is_active=(data.get('program_id') == active_program_id),
                        weeks_completed=data.get('weeks_completed', 0),
                        total_weeks=len(data.get('weeks', []))
                    ))
            except Exception as e:
                print(f"Error reading {program_file}: {e}")
                continue

        return programs

    def update_progress(self, program_id: str, weeks_completed: int) -> bool:
        """Update completion progress for a program"""
        program = self.get_program(program_id)
        if not program:
            return False

        program['weeks_completed'] = weeks_completed

        # Save updated program
        program_file = self.programs_dir / f"program_{program_id}.json"
        with open(program_file, 'w') as f:
            json.dump(program, f, indent=2)

        return True

    def delete_program(self, program_id: str) -> bool:
        """Delete a program"""
        program_file = self.programs_dir / f"program_{program_id}.json"

        if not program_file.exists():
            return False

        # Don't delete if it's the active program
        active = self.get_active_program()
        if active and active.get('program_id') == program_id:
            return False

        program_file.unlink()
        return True

    def archive_program(self, program_id: str) -> bool:
        """Mark program as archived (completed)"""
        program = self.get_program(program_id)
        if not program:
            return False

        program['archived'] = True
        program['archived_at'] = datetime.now().isoformat()

        # Save updated program
        program_file = self.programs_dir / f"program_{program_id}.json"
        with open(program_file, 'w') as f:
            json.dump(program, f, indent=2)

        return True


if __name__ == "__main__":
    # Test program manager
    print("=== Program Manager Test ===\n")

    manager = ProgramManager()

    # Test 1: Save a program
    print("TEST 1: Save a test program")
    print("=" * 60)

    test_program = {
        'template_name': 'upper_lower_4x',
        'start_date': date.today().isoformat(),
        'weeks': [{'week_number': i} for i in range(1, 7)],
        'equipment_used': ['dumbbells', 'bench'],
        'coverage_report': {}
    }

    program_id = manager.save_program(test_program)
    print(f"✅ Saved program: {program_id}\n")

    # Test 2: List programs
    print("TEST 2: List all programs")
    print("=" * 60)
    programs = manager.list_programs()
    for p in programs:
        status = "🟢 ACTIVE" if p.is_active else "⚪"
        print(f"{status} {p.program_id}: {p.template_name.replace('_', ' ').title()}")
        print(f"   Start: {p.start_date} | Progress: {p.weeks_completed}/{p.total_weeks} weeks")
    print()

    # Test 3: Get active program
    print("TEST 3: Get active program")
    print("=" * 60)
    active = manager.get_active_program()
    if active:
        print(f"Active: {active['program_id']}")
        print(f"Template: {active['template_name']}")
    print()

    # Test 4: Update progress
    print("TEST 4: Update progress")
    print("=" * 60)
    manager.update_progress(program_id, weeks_completed=2)
    print(f"✅ Updated progress to 2/6 weeks")
