# Health Insurance Assistant Bot

A Rasa-based chatbot that helps users access their health insurance information through a conversational interface. The bot implements authentication flows and provides policy status information for authenticated users.

## Features

- User Authentication
- Policy Status Checking (for authenticated users)
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
- Checks if user's policy is currently active
- Returns appropriate message based on policy status

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
- `current_date`: Tracks current session date
- `is_policy_active`: Indicates policy status

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
   - Flow guards prevent unauthorized access

## Response Handling

- Contextual responses based on authentication status
- Different capability descriptions for authenticated vs unauthenticated users

## Technical Requirements

- Python
- Rasa Framework
- External Dependencies:
  - requests
  - pendulum 