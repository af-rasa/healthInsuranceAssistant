# Health Insurance Assistant Bot

A Rasa-based chatbot that helps users access their health insurance information through a conversational interface. The bot implements authentication flows and provides policy status information for authenticated users.

## Features

- User Authentication
- Policy Status Checking (for authenticated users)
  - Support for primary and child accounts
  - Interactive button selection for multiple accounts
- Office Hours Information
- Session Management

## Core Functionality

### Authentication Flow
- Users must authenticate before accessing protected features
- Authentication requires:
  - Member ID verification
  - Date of Birth (DOB) verification
- Authentication status is tracked via the `auth_status` slot
- Flow guard prevents authentication loops and unauthorized access to protected features/flows

### Protected Features

#### Policy Status Check
- Available only to authenticated users
- Supports multiple account management:
  - Primary account holder can view their own policy status
  - If child accounts exist, provides interactive buttons to select specific account
  - Dynamically generates account selection interface based on available accounts
- Checks if selected policy is currently active
- Returns personalized message based on policy status and account holder name

### Public Features

#### Office Hours
- Available to all users
- Provides standard office hours information
- No authentication required

## Technical Implementation

### Slot Management
- `auth_status`: Tracks user authentication state
- `member_found`: Indicates if member ID exists in system
- `member_id`: Stores user's member ID
- `dob_input`: Stores user's provided DOB
- `member_name`: Stores authenticated user's name
- `member_dob`: Stores verified DOB from system
- `policy_end_date`: Stores policy expiration date
- `has_child_accounts`: Indicates if user has associated child accounts
- `child_accounts`: Stores array of child account details
- `selected_account_id`: Tracks selected account for policy status check
- `is_policy_active`: Indicates policy status

### Interactive Components
- Dynamic button generation for account selection
- Custom actions for handling multi-account scenarios
- Interactive policy status checking for all associated accounts

### Session Management
- Implements custom session start action
- Maintains persistent slots across sessions
- Tracks current date using Pendulum library

### External Integration
- Connects to external API (JSONbin) for member verification
- Implements secure API key management

## Flow Structure

1. **Initial Greeting**
   - Bot introduces itself
   - Provides available options based on authentication status

2. **Authentication Process**
   - Collects member ID
   - Verifies member exists in system
   - Collects and verifies DOB
   - Updates authentication status

3. **Protected Actions**
   - Policy status checks require authentication
   - Account selection interface for users with child accounts
   - Flow guards prevent unauthorized access

## Response Handling

- Contextual responses based on authentication status
- Different capability descriptions for authenticated vs unauthenticated users
- Account-specific policy status messages

## Technical Requirements

- Python
- Rasa Framework
- External Dependencies:
  - requests
  - pendulum 