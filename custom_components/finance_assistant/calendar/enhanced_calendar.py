"""Enhanced calendar for Finance Assistant integration."""
from __future__ import annotations
import logging
from datetime import datetime, date, timedelta
from typing import Any, List, Optional

from homeassistant.components.calendar import (
    CalendarEntity,
    CalendarEvent,
    CalendarEventDeviceClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..coordinator import FinanceAssistantCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up enhanced financial calendar."""
    coordinator: FinanceAssistantCoordinator = hass.data["finance_assistant"][config_entry.entry_id]["coordinator"]
    
    # Create enhanced calendar entities
    calendars = [
        EnhancedFinancialCalendar(coordinator, "Enhanced Financial Calendar"),
        PendingTransactionsCalendar(coordinator, "Pending Transactions"),
        ScheduledTransactionsCalendar(coordinator, "Scheduled Transactions"),
        RecurringTransactionsCalendar(coordinator, "Recurring Transactions"),
        CriticalExpensesCalendar(coordinator, "Critical Expenses"),
    ]
    
    async_add_entities(calendars)


class EnhancedFinancialCalendar(CoordinatorEntity, CalendarEntity):
    """Enhanced financial calendar showing all transaction types."""
    
    def __init__(self, coordinator: FinanceAssistantCoordinator, name: str) -> None:
        """Initialize the enhanced calendar."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{name.lower().replace(' ', '_')}"
        self._attr_device_class = CalendarEventDeviceClass.CALENDAR
        self._attr_icon = "mdi:calendar-multiple"
    
    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        """Get calendar events for the specified date range."""
        try:
            # Convert datetime to date for comparison
            start_date_date = start_date.date()
            end_date_date = end_date.date()
            
            events = []
            
            # Get enhanced transactions from coordinator
            if not self.coordinator.data:
                return events
            
            enhanced_transactions = self.coordinator.data.get("enhanced_transactions", [])
            recurring_transactions = self.coordinator.data.get("recurring_transactions", [])
            
            # Process enhanced transactions
            for transaction in enhanced_transactions:
                event = self._create_event_from_transaction(transaction, start_date_date, end_date_date)
                if event:
                    events.append(event)
            
            # Process recurring transactions and generate future events
            for recurring in recurring_transactions:
                if recurring.get("is_active", True):
                    recurring_events = self._generate_recurring_events(
                        recurring, start_date_date, end_date_date
                    )
                    events.extend(recurring_events)
            
            # Sort events by start date
            events.sort(key=lambda x: x.start)
            
            _LOGGER.debug("Generated %d calendar events for %s to %s", 
                         len(events), start_date_date, end_date_date)
            
            return events
            
        except Exception as e:
            _LOGGER.error("Error getting enhanced calendar events: %s", e)
            return []
    
    def _create_event_from_transaction(
        self, transaction: dict, start_date: date, end_date: date
    ) -> Optional[CalendarEvent]:
        """Create a calendar event from a transaction."""
        try:
            # Get transaction date
            transaction_date = self._parse_transaction_date(transaction)
            if not transaction_date:
                return None
            
            # Check if transaction is in the requested date range
            if not (start_date <= transaction_date <= end_date):
                return None
            
            # Create event title
            title = self._create_event_title(transaction)
            
            # Create event description
            description = self._create_event_description(transaction)
            
            # Determine event color based on transaction type
            color = self._get_event_color(transaction)
            
            # Create calendar event
            event = CalendarEvent(
                summary=title,
                description=description,
                start=transaction_date,
                end=transaction_date,
                location=transaction.get("account_name", ""),
                uid=f"fa_{transaction.get('id', 'unknown')}",
                rrule=None,  # No recurrence for individual transactions
                color=color,
            )
            
            return event
            
        except Exception as e:
            _LOGGER.error("Error creating event from transaction: %s", e)
            return None
    
    def _generate_recurring_events(
        self, recurring: dict, start_date: date, end_date: date
    ) -> List[CalendarEvent]:
        """Generate calendar events for recurring transactions."""
        events = []
        
        try:
            # Get recurring transaction details
            frequency = recurring.get("frequency", "monthly")
            start_date_recurring = self._parse_date(recurring.get("start_date"))
            end_date_recurring = self._parse_date(recurring.get("end_date"))
            amount = recurring.get("amount", 0)
            category_name = recurring.get("category_name", "Unknown")
            payee_name = recurring.get("payee_name", "Unknown")
            account_name = recurring.get("account_name", "Unknown")
            
            if not start_date_recurring:
                return events
            
            # Generate events based on frequency
            current_date = start_date_recurring
            while current_date <= end_date:
                # Check if this date is in our requested range
                if start_date <= current_date <= end_date:
                    # Create event for this occurrence
                    title = f"Recurring: {payee_name} - {category_name}"
                    description = f"Amount: ${amount:.2f}\nAccount: {account_name}\nType: {recurring.get('transaction_type', 'expense')}"
                    
                    event = CalendarEvent(
                        summary=title,
                        description=description,
                        start=current_date,
                        end=current_date,
                        location=account_name,
                        uid=f"fa_recurring_{recurring.get('id', 'unknown')}_{current_date.isoformat()}",
                        rrule=None,
                        color="#FF9800",  # Orange for recurring
                    )
                    
                    events.append(event)
                
                # Move to next occurrence
                current_date = self._get_next_occurrence(current_date, frequency)
                
                # Safety check to prevent infinite loops
                if current_date > end_date_recurring or current_date > end_date + timedelta(days=365):
                    break
            
        except Exception as e:
            _LOGGER.error("Error generating recurring events: %s", e)
        
        return events
    
    def _get_next_occurrence(self, current_date: date, frequency: str) -> date:
        """Get the next occurrence date based on frequency."""
        if frequency == "daily":
            return current_date + timedelta(days=1)
        elif frequency == "weekly":
            return current_date + timedelta(weeks=1)
        elif frequency == "biweekly":
            return current_date + timedelta(weeks=2)
        elif frequency == "monthly":
            # Simple monthly increment (not perfect for all months)
            year = current_date.year
            month = current_date.month
            day = current_date.day
            
            month += 1
            if month > 12:
                month = 1
                year += 1
            
            # Handle month length differences
            try:
                return date(year, month, day)
            except ValueError:
                # If day doesn't exist in new month, use last day of month
                if month == 12:
                    return date(year + 1, 1, 1) - timedelta(days=1)
                else:
                    return date(year, month + 1, 1) - timedelta(days=1)
        elif frequency == "quarterly":
            return current_date + timedelta(days=90)
        elif frequency == "yearly":
            return current_date + timedelta(days=365)
        else:
            # Default to monthly
            return current_date + timedelta(days=30)
    
    def _parse_transaction_date(self, transaction: dict) -> Optional[date]:
        """Parse transaction date from various possible formats."""
        # Try different date fields
        date_fields = ["date", "transaction_date", "due_date", "created_at"]
        
        for field in date_fields:
            if field in transaction:
                parsed_date = self._parse_date(transaction[field])
                if parsed_date:
                    return parsed_date
        
        return None
    
    def _parse_date(self, date_value: Any) -> Optional[date]:
        """Parse date from various formats."""
        if not date_value:
            return None
        
        try:
            if isinstance(date_value, str):
                # Try ISO format first
                if "T" in date_value:
                    return datetime.fromisoformat(date_value.replace("Z", "+00:00")).date()
                else:
                    return datetime.strptime(date_value, "%Y-%m-%d").date()
            elif isinstance(date_value, datetime):
                return date_value.date()
            elif isinstance(date_value, date):
                return date_value
        except (ValueError, TypeError):
            _LOGGER.warning("Could not parse date: %s", date_value)
        
        return None
    
    def _create_event_title(self, transaction: dict) -> str:
        """Create event title from transaction data."""
        payee = transaction.get("payee_name", "Unknown")
        category = transaction.get("category_name", "Unknown")
        amount = transaction.get("amount", 0)
        status = transaction.get("status", "unknown")
        
        # Format amount
        amount_str = f"${abs(amount):.2f}"
        if amount < 0:
            amount_str = f"-{amount_str}"
        
        # Create title based on status
        if status == "pending":
            return f"Pending: {payee} - {amount_str}"
        elif status == "scheduled":
            return f"Scheduled: {payee} - {amount_str}"
        elif status == "real":
            return f"{payee} - {amount_str}"
        else:
            return f"{payee} - {category} - {amount_str}"
    
    def _create_event_description(self, transaction: dict) -> str:
        """Create event description from transaction data."""
        lines = []
        
        # Basic transaction info
        amount = transaction.get("amount", 0)
        amount_str = f"${abs(amount):.2f}"
        if amount < 0:
            amount_str = f"-{amount_str}"
        
        lines.append(f"Amount: {amount_str}")
        
        # Category and payee
        category = transaction.get("category_name")
        if category:
            lines.append(f"Category: {category}")
        
        payee = transaction.get("payee_name")
        if payee:
            lines.append(f"Payee: {payee}")
        
        # Account
        account = transaction.get("account_name")
        if account:
            lines.append(f"Account: {account}")
        
        # Status
        status = transaction.get("status", "unknown")
        lines.append(f"Status: {status.title()}")
        
        # Source type
        source_type = transaction.get("source_type")
        if source_type:
            lines.append(f"Source: {source_type.title()}")
        
        # Notes
        notes = transaction.get("notes")
        if notes:
            lines.append(f"Notes: {notes}")
        
        return "\n".join(lines)
    
    def _get_event_color(self, transaction: dict) -> str:
        """Get event color based on transaction characteristics."""
        status = transaction.get("status", "unknown")
        amount = transaction.get("amount", 0)
        
        # Color by status
        if status == "pending":
            return "#FFC107"  # Amber
        elif status == "scheduled":
            return "#2196F3"  # Blue
        elif status == "real":
            # Color by amount (positive/negative)
            if amount > 0:
                return "#4CAF50"  # Green (income)
            else:
                return "#F44336"  # Red (expense)
        else:
            return "#9E9E9E"  # Grey


class PendingTransactionsCalendar(CoordinatorEntity, CalendarEntity):
    """Calendar showing only pending transactions."""
    
    def __init__(self, coordinator: FinanceAssistantCoordinator, name: str) -> None:
        """Initialize the pending transactions calendar."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{name.lower().replace(' ', '_')}"
        self._attr_device_class = CalendarEventDeviceClass.CALENDAR
        self._attr_icon = "mdi:clock-outline"
    
    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        """Get pending transaction events."""
        try:
            start_date_date = start_date.date()
            end_date_date = end_date.date()
            
            events = []
            
            if not self.coordinator.data:
                return events
            
            enhanced_transactions = self.coordinator.data.get("enhanced_transactions", [])
            
            # Filter for pending transactions only
            pending_transactions = [
                t for t in enhanced_transactions 
                if t.get("status") == "pending"
            ]
            
            # Create events for pending transactions
            for transaction in pending_transactions:
                event = self._create_pending_event(transaction, start_date_date, end_date_date)
                if event:
                    events.append(event)
            
            events.sort(key=lambda x: x.start)
            return events
            
        except Exception as e:
            _LOGGER.error("Error getting pending transaction events: %s", e)
            return []
    
    def _create_pending_event(
        self, transaction: dict, start_date: date, end_date: date
    ) -> Optional[CalendarEvent]:
        """Create a calendar event for a pending transaction."""
        # Similar to the main calendar but focused on pending transactions
        # Implementation would be similar to _create_event_from_transaction
        pass


class ScheduledTransactionsCalendar(CoordinatorEntity, CalendarEntity):
    """Calendar showing only scheduled transactions."""
    
    def __init__(self, coordinator: FinanceAssistantCoordinator, name: str) -> None:
        """Initialize the scheduled transactions calendar."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{name.lower().replace(' ', '_')}"
        self._attr_device_class = CalendarEventDeviceClass.CALENDAR
        self._attr_icon = "mdi:calendar-clock"
    
    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        """Get scheduled transaction events."""
        # Implementation similar to PendingTransactionsCalendar
        pass


class RecurringTransactionsCalendar(CoordinatorEntity, CalendarEntity):
    """Calendar showing recurring transaction templates."""
    
    def __init__(self, coordinator: FinanceAssistantCoordinator, name: str) -> None:
        """Initialize the recurring transactions calendar."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{name.lower().replace(' ', '_')}"
        self._attr_device_class = CalendarEventDeviceClass.CALENDAR
        self._attr_icon = "mdi:calendar-repeat"
    
    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        """Get recurring transaction events."""
        # Implementation would show recurring transaction templates
        pass


class CriticalExpensesCalendar(CoordinatorEntity, CalendarEntity):
    """Calendar showing critical upcoming expenses."""
    
    def __init__(self, coordinator: FinanceAssistantCoordinator, name: str) -> None:
        """Initialize the critical expenses calendar."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{name.lower().replace(' ', '_')}"
        self._attr_device_class = CalendarEventDeviceClass.CALENDAR
        self._attr_icon = "mdi:alert-circle"
    
    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> List[CalendarEvent]:
        """Get critical expense events."""
        # Implementation would show critical expenses from the coordinator data
        pass
