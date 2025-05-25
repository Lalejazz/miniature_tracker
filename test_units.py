#!/usr/bin/env python3
"""
Test script to add sample units to the miniature tracker for testing the new Unit system.
"""

import asyncio
import json
from uuid import uuid4
from decimal import Decimal

# Add the backend directory to the path
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import get_database
from app.models import UnitCreate, PaintingStatus, GameSystem, UnitType, BaseDimension

async def create_sample_units():
    """Create sample units for testing."""
    
    # Initialize database
    db = get_database()
    await db.initialize()
    
    # Sample user ID (you'll need to replace this with a real user ID from your database)
    # For testing, let's create a test user first
    from app.auth_models import UserCreate
    
    try:
        # Try to create a test user
        test_user = await db.create_user(UserCreate(
            email="test@example.com",
            password="testpassword123"
        ))
        user_id = test_user.id
        print(f"Created test user: {test_user.email}")
    except Exception as e:
        # If user already exists, get existing users and use the first one
        users = await db.get_all_users()
        if users:
            user_id = users[0].id
            print(f"Using existing user: {users[0].email}")
        else:
            print("No users found and couldn't create test user")
            return
    
    # Sample units to create
    sample_units = [
        # Warhammer 40k Units
        UnitCreate(
            name="Space Marine Tactical Squad",
            game_system=GameSystem.WARHAMMER_40K,
            faction="Ultramarines",
            unit_type=UnitType.INFANTRY,
            quantity=10,
            base_dimension=BaseDimension.ROUND_32MM,
            cost=Decimal("55.00"),
            status=PaintingStatus.ASSEMBLED,
            notes="Classic tactical marines with bolters"
        ),
        UnitCreate(
            name="Ork Boyz",
            game_system=GameSystem.WARHAMMER_40K,
            faction="Orks",
            unit_type=UnitType.INFANTRY,
            quantity=20,
            base_dimension=BaseDimension.ROUND_32MM,
            cost=Decimal("40.00"),
            status=PaintingStatus.PRIMED,
            notes="WAAAGH! Green tide incoming"
        ),
        UnitCreate(
            name="Imperial Knight",
            game_system=GameSystem.WARHAMMER_40K,
            faction="Imperial Knights",
            unit_type=UnitType.VEHICLE,
            quantity=1,
            base_dimension=BaseDimension.OVAL_170X105MM,
            cost=Decimal("170.00"),
            status=PaintingStatus.GAME_READY,
            notes="House Terryn Knight Paladin"
        ),
        UnitCreate(
            name="Necron Warriors",
            game_system=GameSystem.WARHAMMER_40K,
            faction="Necrons",
            unit_type=UnitType.INFANTRY,
            quantity=20,
            base_dimension=BaseDimension.ROUND_32MM,
            cost=Decimal("45.00"),
            status=PaintingStatus.PURCHASED,
            notes="Silent death from the tomb worlds"
        ),
        
        # Age of Sigmar Units
        UnitCreate(
            name="Stormcast Liberators",
            game_system=GameSystem.AGE_OF_SIGMAR,
            faction="Stormcast Eternals",
            unit_type=UnitType.INFANTRY,
            quantity=5,
            base_dimension=BaseDimension.ROUND_40MM,
            cost=Decimal("60.00"),
            status=PaintingStatus.PARADE_READY,
            notes="Golden warriors of Sigmar"
        ),
        UnitCreate(
            name="Bloodthirster",
            game_system=GameSystem.AGE_OF_SIGMAR,
            faction="Khorne Daemons",
            unit_type=UnitType.MONSTER,
            quantity=1,
            base_dimension=BaseDimension.OVAL_120X92MM,
            cost=Decimal("140.00"),
            status=PaintingStatus.ASSEMBLED,
            notes="Greater Daemon of Khorne"
        ),
        UnitCreate(
            name="Skeleton Warriors",
            game_system=GameSystem.AGE_OF_SIGMAR,
            faction="Legions of Nagash",
            unit_type=UnitType.INFANTRY,
            quantity=20,
            base_dimension=BaseDimension.ROUND_25MM,
            cost=Decimal("35.00"),
            status=PaintingStatus.PRIMED,
            notes="Undead legion rising"
        ),
        
        # D&D Units
        UnitCreate(
            name="Ancient Red Dragon",
            game_system=GameSystem.DND_RPG,
            faction="Dragons",
            unit_type=UnitType.MONSTER,
            quantity=1,
            base_dimension=BaseDimension.ROUND_50MM,
            cost=Decimal("80.00"),
            status=PaintingStatus.GAME_READY,
            notes="Legendary ancient wyrm"
        ),
        UnitCreate(
            name="Human Fighter",
            game_system=GameSystem.DND_RPG,
            faction="Adventurers",
            unit_type=UnitType.CHARACTER,
            quantity=1,
            base_dimension=BaseDimension.ROUND_25MM,
            cost=Decimal("15.00"),
            status=PaintingStatus.PARADE_READY,
            notes="Player character miniature"
        ),
        UnitCreate(
            name="Orc Warband",
            game_system=GameSystem.DND_RPG,
            faction="Orcs",
            unit_type=UnitType.INFANTRY,
            quantity=8,
            base_dimension=BaseDimension.ROUND_25MM,
            cost=Decimal("25.00"),
            status=PaintingStatus.WANT_TO_BUY,
            notes="Savage orc raiders"
        ),
        
        # Other/Custom Units
        UnitCreate(
            name="Terrain Piece - Ruined Building",
            game_system=GameSystem.OTHER,
            faction="Terrain",
            unit_type=UnitType.TERRAIN,
            quantity=1,
            base_dimension=BaseDimension.CUSTOM,
            custom_base_size="6x4 inch base",
            cost=Decimal("30.00"),
            status=PaintingStatus.ASSEMBLED,
            notes="Gothic ruins for battlefield"
        ),
    ]
    
    print(f"\nCreating {len(sample_units)} sample units...")
    
    created_units = []
    for unit_data in sample_units:
        try:
            unit = await db.create_miniature(unit_data, user_id)
            created_units.append(unit)
            print(f"✅ Created: {unit.name} ({unit.game_system.value})")
        except Exception as e:
            print(f"❌ Failed to create {unit_data.name}: {e}")
    
    print(f"\n🎉 Successfully created {len(created_units)} units!")
    print(f"📊 You can now test the statistics dashboard with real data.")
    
    # Print summary
    print("\n📋 Summary:")
    game_systems = {}
    statuses = {}
    total_cost = 0
    total_models = 0
    
    for unit in created_units:
        # Game systems
        system = unit.game_system.value if unit.game_system else 'unknown'
        game_systems[system] = game_systems.get(system, 0) + 1
        
        # Statuses
        status = unit.status.value
        statuses[status] = statuses.get(status, 0) + 1
        
        # Totals
        if unit.cost:
            total_cost += float(unit.cost)
        total_models += unit.quantity
    
    print(f"  • Total Units: {len(created_units)}")
    print(f"  • Total Models: {total_models}")
    print(f"  • Total Cost: ${total_cost:.2f}")
    print(f"  • Game Systems: {dict(game_systems)}")
    print(f"  • Status Distribution: {dict(statuses)}")

if __name__ == "__main__":
    asyncio.run(create_sample_units()) 