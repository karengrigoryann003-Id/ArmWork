/* ============================================================================
   ArmWork SQLite Schema
   Local թեստի դատարկ database կառուցվածք Python 3.14-ի համար։
   Այս ֆայլը table-ներ է ստեղծում, բայց ոչ մի demo/test տվյալ չի ավելացնում։
   ============================================================================ */

PRAGMA foreign_keys = ON;

/* Օգտատերեր՝ և՛ ֆրիլանսեր, և՛ պատվիրատու */
CREATE TABLE IF NOT EXISTS Users (
    UserId INTEGER PRIMARY KEY AUTOINCREMENT,
    Role TEXT NOT NULL CHECK (Role IN ('freelancer', 'client')),
    Username TEXT NOT NULL UNIQUE,
    Email TEXT NOT NULL UNIQUE,
    PasswordHash TEXT NOT NULL,
    FullName TEXT NOT NULL,
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

/* Ֆրիլանսերի լրացուցիչ տվյալներ */
CREATE TABLE IF NOT EXISTS FreelancerProfiles (
    UserId INTEGER PRIMARY KEY,
    Specialty TEXT,
    Bio TEXT,
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserId) REFERENCES Users(UserId)
);

/* Պատվիրատուի / ընկերության լրացուցիչ տվյալներ */
CREATE TABLE IF NOT EXISTS ClientProfiles (
    UserId INTEGER PRIMARY KEY,
    CompanyName TEXT,
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserId) REFERENCES Users(UserId)
);

/* Պատվիրատուի տեղադրած աշխատանքներ */
CREATE TABLE IF NOT EXISTS Jobs (
    JobId INTEGER PRIMARY KEY AUTOINCREMENT,
    ClientId INTEGER NOT NULL,
    Title TEXT NOT NULL,
    Description TEXT NOT NULL,
    Category TEXT,
    BudgetAmount REAL,
    Status TEXT NOT NULL DEFAULT 'open',
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ClientId) REFERENCES Users(UserId)
);

/* Ֆրիլանսերների դիմումներ աշխատանքներին */
CREATE TABLE IF NOT EXISTS JobApplications (
    ApplicationId INTEGER PRIMARY KEY AUTOINCREMENT,
    JobId INTEGER NOT NULL,
    FreelancerId INTEGER NOT NULL,
    ProposalText TEXT NOT NULL,
    BidAmount REAL,
    DeliveryTime TEXT,
    PortfolioUrl TEXT,
    Status TEXT NOT NULL DEFAULT 'pending',
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (JobId) REFERENCES Jobs(JobId),
    FOREIGN KEY (FreelancerId) REFERENCES Users(UserId)
);

/* Chat conversation-ի գլխավոր գրառում */
CREATE TABLE IF NOT EXISTS Conversations (
    ConversationId INTEGER PRIMARY KEY AUTOINCREMENT,
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

/* Conversation-ի մասնակիցներ */
CREATE TABLE IF NOT EXISTS ConversationParticipants (
    ConversationId INTEGER NOT NULL,
    UserId INTEGER NOT NULL,
    LastReadAt TEXT,
    PRIMARY KEY (ConversationId, UserId),
    FOREIGN KEY (ConversationId) REFERENCES Conversations(ConversationId),
    FOREIGN KEY (UserId) REFERENCES Users(UserId)
);

/* Chat-ի հաղորդագրություններ */
CREATE TABLE IF NOT EXISTS Messages (
    MessageId INTEGER PRIMARY KEY AUTOINCREMENT,
    ConversationId INTEGER NOT NULL,
    SenderId INTEGER NOT NULL,
    Body TEXT NOT NULL,
    CreatedAt TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    IsRead INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (ConversationId) REFERENCES Conversations(ConversationId),
    FOREIGN KEY (SenderId) REFERENCES Users(UserId)
);

/* Արագ որոնման index-ներ */
CREATE INDEX IF NOT EXISTS IX_Users_Username ON Users(Username);
CREATE INDEX IF NOT EXISTS IX_Messages_Conversation_CreatedAt ON Messages(ConversationId, CreatedAt);
