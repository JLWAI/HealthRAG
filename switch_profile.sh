#!/bin/bash

# Profile Switcher for HealthRAG Multi-User
# Allows easy switching between family member profiles

PROFILES_DIR="data/profiles"
ACTIVE_PROFILE="data/user_profile.json"

# Ensure profiles directory exists
mkdir -p "$PROFILES_DIR"

# Function to list available profiles
list_profiles() {
    echo "Available profiles:"
    if [ -d "$PROFILES_DIR" ] && [ "$(ls -A $PROFILES_DIR/*.json 2>/dev/null)" ]; then
        for profile in "$PROFILES_DIR"/*.json; do
            name=$(basename "$profile" .json)
            echo "  - $name"
        done
    else
        echo "  (No saved profiles found)"
    fi
}

# Function to save current profile
save_current() {
    if [ ! -f "$ACTIVE_PROFILE" ]; then
        echo "❌ No active profile to save"
        return 1
    fi

    if [ -z "$1" ]; then
        echo "❌ Please provide a name for this profile"
        echo "Usage: $0 save <name>"
        return 1
    fi

    cp "$ACTIVE_PROFILE" "$PROFILES_DIR/$1.json"
    echo "✅ Saved current profile as: $1"
}

# Function to switch to a profile
switch_to() {
    if [ -z "$1" ]; then
        echo "❌ Please specify a profile name"
        list_profiles
        return 1
    fi

    profile_file="$PROFILES_DIR/$1.json"

    if [ ! -f "$profile_file" ]; then
        echo "❌ Profile '$1' not found"
        list_profiles
        return 1
    fi

    # Backup current active profile if it exists
    if [ -f "$ACTIVE_PROFILE" ]; then
        current_name=$(grep -o '"name": "[^"]*"' "$ACTIVE_PROFILE" | cut -d'"' -f4)
        if [ ! -z "$current_name" ] && [ "$current_name" != "$1" ]; then
            echo "💾 Backing up current profile ($current_name)"
            cp "$ACTIVE_PROFILE" "$PROFILES_DIR/${current_name}.json"
        fi
    fi

    # Switch to new profile
    cp "$profile_file" "$ACTIVE_PROFILE"
    echo "✅ Switched to profile: $1"

    # Show profile info
    if command -v jq &> /dev/null; then
        name=$(jq -r '.personal_info.name' "$ACTIVE_PROFILE")
        phase=$(jq -r '.goals.phase' "$ACTIVE_PROFILE")
        equipment_count=$(jq -r '.equipment | length' "$ACTIVE_PROFILE")
        echo ""
        echo "📋 Active Profile:"
        echo "   Name: $name"
        echo "   Phase: $phase"
        echo "   Equipment: $equipment_count items"
    fi
}

# Function to create new profile
create_profile() {
    echo "🆕 Creating new profile..."
    echo ""
    echo "Steps:"
    echo "1. Open the Streamlit app"
    echo "2. Delete current profile (if exists) in sidebar"
    echo "3. Complete the onboarding wizard"
    echo "4. Run: $0 save <name>"
    echo ""
    echo "Or press Ctrl+C to cancel and run Streamlit now..."

    sleep 2
    echo ""
    echo "Starting Streamlit..."
    streamlit run src/main.py
}

# Main script logic
case "$1" in
    list)
        list_profiles
        ;;
    save)
        save_current "$2"
        ;;
    switch)
        switch_to "$2"
        ;;
    new|create)
        create_profile
        ;;
    *)
        echo "HealthRAG Profile Switcher"
        echo ""
        echo "Usage:"
        echo "  $0 list              - List all saved profiles"
        echo "  $0 switch <name>     - Switch to a profile"
        echo "  $0 save <name>       - Save current active profile"
        echo "  $0 new               - Create a new profile"
        echo ""
        echo "Examples:"
        echo "  $0 switch jason      - Switch to Jason's profile"
        echo "  $0 switch sarah      - Switch to Sarah's profile"
        echo "  $0 save jason        - Save current profile as 'jason'"
        echo ""
        list_profiles
        ;;
esac
