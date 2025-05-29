import random
from datetime import datetime, timedelta
from stinkworld.utils.debug import debug_log

class Economy:
    """Manages game economy, shops, jobs, and trading."""
    
    def __init__(self):
        self.currency_name = "Credits"
        self.inflation_rate = 0.001  # Daily inflation rate
        self.market_volatility = 0.05  # Market price fluctuation range
        
        # Initialize job market
        self.jobs = {
            'Store Clerk': {
                'salary': 50,
                'hours': 8,
                'requirements': {'book_smarts': 2},
                'reputation_gain': 1,
                'stress': 2
            },
            'Security Guard': {
                'salary': 70,
                'hours': 8,
                'requirements': {'strength': 3},
                'reputation_gain': 2,
                'stress': 3
            },
            'Office Worker': {
                'salary': 80,
                'hours': 8,
                'requirements': {'book_smarts': 4},
                'reputation_gain': 2,
                'stress': 4
            },
            'Street Vendor': {
                'salary': 40,
                'hours': 6,
                'requirements': {'street_smarts': 2},
                'reputation_gain': 1,
                'stress': 2
            },
            'Bouncer': {
                'salary': 90,
                'hours': 6,
                'requirements': {'strength': 4, 'street_smarts': 2},
                'reputation_gain': 3,
                'stress': 4
            },
            'Taxi Driver': {
                'salary': 60,
                'hours': 8,
                'requirements': {'street_smarts': 3},
                'reputation_gain': 2,
                'stress': 3
            }
        }
        
        # Initialize items and their base prices
        self.items = {
            # Food and Drinks
            'Sandwich': {'base_price': 5, 'category': 'food', 'effect': {'hunger': 20}},
            'Energy Drink': {'base_price': 3, 'category': 'drink', 'effect': {'energy': 30}},
            'Coffee': {'base_price': 2, 'category': 'drink', 'effect': {'energy': 15}},
            'Pizza Slice': {'base_price': 4, 'category': 'food', 'effect': {'hunger': 25}},
            'Water Bottle': {'base_price': 1, 'category': 'drink', 'effect': {'thirst': 30}},
            
            # Clothing
            'Basic Shirt': {'base_price': 15, 'category': 'clothing', 'style': 1},
            'Nice Pants': {'base_price': 25, 'category': 'clothing', 'style': 2},
            'Fancy Jacket': {'base_price': 50, 'category': 'clothing', 'style': 3},
            'Running Shoes': {'base_price': 30, 'category': 'clothing', 'speed_bonus': 1},
            
            # Tools and Items
            'Lockpick': {'base_price': 20, 'category': 'tool', 'illegal': True},
            'Phone': {'base_price': 100, 'category': 'electronics'},
            'Watch': {'base_price': 40, 'category': 'accessories'},
            'Backpack': {'base_price': 35, 'category': 'accessories', 'inventory_bonus': 5},
            
            # Medical
            'Bandage': {'base_price': 5, 'category': 'medical', 'heal': 10},
            'Pain Pills': {'base_price': 15, 'category': 'medical', 'heal': 20},
            'First Aid Kit': {'base_price': 30, 'category': 'medical', 'heal': 50}
        }
        
        # Initialize shops
        self.shops = {
            'Convenience Store': {
                'items': ['Sandwich', 'Energy Drink', 'Coffee', 'Water Bottle', 'Basic Shirt'],
                'markup': 1.2,
                'hours': {'open': 6, 'close': 22}
            },
            'Clothing Store': {
                'items': ['Basic Shirt', 'Nice Pants', 'Fancy Jacket', 'Running Shoes'],
                'markup': 1.5,
                'hours': {'open': 9, 'close': 18}
            },
            'Electronics Shop': {
                'items': ['Phone', 'Watch'],
                'markup': 1.4,
                'hours': {'open': 10, 'close': 20}
            },
            'Medical Supply': {
                'items': ['Bandage', 'Pain Pills', 'First Aid Kit'],
                'markup': 1.3,
                'hours': {'open': 8, 'close': 20}
            },
            'Black Market': {
                'items': ['Lockpick'],
                'markup': 2.0,
                'hours': {'open': 22, 'close': 4},
                'illegal': True
            }
        }
        
        # Market prices start at base prices
        self.current_prices = {item: info['base_price'] for item, info in self.items.items()}
        self.last_price_update = datetime.now()

    def update_prices(self, current_date):
        """Update prices based on time passed and market conditions."""
        days_passed = (current_date - self.last_price_update).days
        if days_passed > 0:
            # Apply inflation
            inflation_factor = (1 + self.inflation_rate) ** days_passed
            
            for item in self.current_prices:
                # Apply inflation
                base_price = self.current_prices[item] * inflation_factor
                
                # Add random market fluctuation
                fluctuation = random.uniform(-self.market_volatility, self.market_volatility)
                self.current_prices[item] = round(base_price * (1 + fluctuation), 2)
            
            self.last_price_update = current_date

    def get_job_requirements(self, job_title):
        """Get requirements for a specific job."""
        return self.jobs.get(job_title, {}).get('requirements', {})

    def can_work_job(self, player, job_title):
        """Check if player meets job requirements."""
        if job_title not in self.jobs:
            return False
            
        requirements = self.get_job_requirements(job_title)
        for stat, required_value in requirements.items():
            if getattr(player, stat, 0) < required_value:
                return False
        return True

    def work_shift(self, player, job_title, hours_worked):
        """Calculate pay and effects for working a shift."""
        if not self.can_work_job(player, job_title):
            return 0, "You don't meet the requirements for this job."
            
        job = self.jobs[job_title]
        base_pay = job['salary'] * hours_worked
        
        # Apply bonuses based on stats
        stat_bonus = 1.0
        for stat, req_value in job['requirements'].items():
            player_stat = getattr(player, stat, 0)
            if player_stat > req_value:
                stat_bonus += 0.1 * (player_stat - req_value)
        
        total_pay = round(base_pay * stat_bonus)
        
        # Apply stress and fatigue
        stress_gain = job['stress'] * hours_worked
        energy_loss = 5 * hours_worked
        
        return total_pay, {
            'stress': stress_gain,
            'energy': -energy_loss,
            'reputation': job['reputation_gain']
        }

    def get_shop_inventory(self, shop_name, current_hour):
        """Get available items in a shop based on operating hours."""
        if shop_name not in self.shops:
            return []
            
        shop = self.shops[shop_name]
        
        # Check if shop is open
        open_hour = shop['hours']['open']
        close_hour = shop['hours']['close']
        if close_hour < open_hour:  # Handles shops open past midnight
            is_open = current_hour >= open_hour or current_hour < close_hour
        else:
            is_open = open_hour <= current_hour < close_hour
            
        if not is_open:
            return []
            
        # Return available items with their current prices
        inventory = []
        for item_name in shop['items']:
            if item_name in self.current_prices:
                price = round(self.current_prices[item_name] * shop['markup'], 2)
                inventory.append({
                    'name': item_name,
                    'price': price,
                    'info': self.items[item_name]
                })
        
        return inventory

    def buy_item(self, player, shop_name, item_name, current_hour):
        """Handle item purchase transaction."""
        inventory = self.get_shop_inventory(shop_name, current_hour)
        item = next((item for item in inventory if item['name'] == item_name), None)
        
        if not item:
            return False, "Item not available in this shop."
            
        if player.money < item['price']:
            return False, "Not enough money."
            
        # Handle illegal items and reputation
        if self.items[item_name].get('illegal', False):
            if player.reputation > -10:  # Too good reputation for black market
                return False, "The merchant doesn't trust you with these goods."
            player.reputation -= 1
            
        # Process transaction
        player.money -= item['price']
        player.inventory.append(item_name)
        
        return True, f"Purchased {item_name} for {item['price']} {self.currency_name}"

    def sell_item(self, player, shop_name, item_name, current_hour):
        """Handle item selling transaction."""
        if item_name not in player.inventory:
            return False, "You don't have this item."
            
        if shop_name not in self.shops:
            return False, "Shop not found."
            
        shop = self.shops[shop_name]
        
        # Check if shop buys this type of item
        if item_name not in shop['items']:
            return False, "This shop doesn't buy this type of item."
            
        # Calculate sell price (usually 50% of buy price)
        sell_price = round(self.current_prices[item_name] * 0.5, 2)
        
        # Process transaction
        player.inventory.remove(item_name)
        player.money += sell_price
        
        return True, f"Sold {item_name} for {sell_price} {self.currency_name}"

    def get_available_jobs(self, player):
        """Get list of jobs the player qualifies for."""
        available_jobs = []
        for job_title, job_info in self.jobs.items():
            if self.can_work_job(player, job_title):
                available_jobs.append({
                    'title': job_title,
                    'salary': job_info['salary'],
                    'hours': job_info['hours'],
                    'requirements': job_info['requirements']
                })
        return available_jobs