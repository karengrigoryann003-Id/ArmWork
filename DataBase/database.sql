/* ============================================================================
   ArmWork Database Schema
   SQL Server-ի դատարկ կառուցվածք ArmWork պրոեկտի համար։
   Այս ֆայլը ստեղծում է միայն table-ները, ոչ մի test/demo տվյալ չի ավելացնում։
   Server՝ localhost,1433
   Database՝ ArmWork
   ============================================================================ */

IF DB_ID(N'ArmWork') IS NULL
BEGIN
    CREATE DATABASE ArmWork;
END
GO

USE ArmWork;
GO

/* Օգտատերեր՝ և՛ ֆրիլանսեր, և՛ պատվիրատու */
IF OBJECT_ID(N'dbo.Users', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Users (
        UserId INT IDENTITY(1,1) PRIMARY KEY,
        Role NVARCHAR(20) NOT NULL,
        Username NVARCHAR(50) NOT NULL UNIQUE,
        Email NVARCHAR(255) NOT NULL UNIQUE,
        PasswordHash NVARCHAR(255) NOT NULL,
        FullName NVARCHAR(150) NOT NULL,
        CreatedAt DATETIME2 NOT NULL CONSTRAINT DF_Users_CreatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT CK_Users_Role CHECK (Role IN (N'freelancer', N'client'))
    );
END
GO

/* Ֆրիլանսերի լրացուցիչ տվյալներ */
IF OBJECT_ID(N'dbo.FreelancerProfiles', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.FreelancerProfiles (
        UserId INT PRIMARY KEY,
        Specialty NVARCHAR(120) NULL,
        Bio NVARCHAR(1000) NULL,
        CreatedAt DATETIME2 NOT NULL CONSTRAINT DF_FreelancerProfiles_CreatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_FreelancerProfiles_Users FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId)
    );
END
GO

/* Պատվիրատուի / ընկերության լրացուցիչ տվյալներ */
IF OBJECT_ID(N'dbo.ClientProfiles', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.ClientProfiles (
        UserId INT PRIMARY KEY,
        CompanyName NVARCHAR(180) NULL,
        CreatedAt DATETIME2 NOT NULL CONSTRAINT DF_ClientProfiles_CreatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_ClientProfiles_Users FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId)
    );
END
GO

/* Պատվիրատուի տեղադրած աշխատանքներ */
IF OBJECT_ID(N'dbo.Jobs', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Jobs (
        JobId INT IDENTITY(1,1) PRIMARY KEY,
        ClientId INT NOT NULL,
        Title NVARCHAR(180) NOT NULL,
        Description NVARCHAR(MAX) NOT NULL,
        Category NVARCHAR(80) NULL,
        BudgetAmount DECIMAL(18,2) NULL,
        Status NVARCHAR(30) NOT NULL CONSTRAINT DF_Jobs_Status DEFAULT N'open',
        CreatedAt DATETIME2 NOT NULL CONSTRAINT DF_Jobs_CreatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_Jobs_Client FOREIGN KEY (ClientId) REFERENCES dbo.Users(UserId)
    );
END
GO

/* Ֆրիլանսերների դիմումներ աշխատանքներին */
IF OBJECT_ID(N'dbo.JobApplications', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.JobApplications (
        ApplicationId INT IDENTITY(1,1) PRIMARY KEY,
        JobId INT NOT NULL,
        FreelancerId INT NOT NULL,
        ProposalText NVARCHAR(MAX) NOT NULL,
        BidAmount DECIMAL(18,2) NULL,
        DeliveryTime NVARCHAR(80) NULL,
        PortfolioUrl NVARCHAR(500) NULL,
        Status NVARCHAR(30) NOT NULL CONSTRAINT DF_JobApplications_Status DEFAULT N'pending',
        CreatedAt DATETIME2 NOT NULL CONSTRAINT DF_JobApplications_CreatedAt DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_JobApplications_Jobs FOREIGN KEY (JobId) REFERENCES dbo.Jobs(JobId),
        CONSTRAINT FK_JobApplications_Freelancers FOREIGN KEY (FreelancerId) REFERENCES dbo.Users(UserId)
    );
END
GO

/* Chat conversation-ի գլխավոր գրառում */
IF OBJECT_ID(N'dbo.Conversations', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Conversations (
        ConversationId INT IDENTITY(1,1) PRIMARY KEY,
        CreatedAt DATETIME2 NOT NULL CONSTRAINT DF_Conversations_CreatedAt DEFAULT SYSUTCDATETIME(),
        UpdatedAt DATETIME2 NOT NULL CONSTRAINT DF_Conversations_UpdatedAt DEFAULT SYSUTCDATETIME()
    );
END
GO

/* Conversation-ի մասնակիցներ */
IF OBJECT_ID(N'dbo.ConversationParticipants', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.ConversationParticipants (
        ConversationId INT NOT NULL,
        UserId INT NOT NULL,
        LastReadAt DATETIME2 NULL,
        PRIMARY KEY (ConversationId, UserId),
        CONSTRAINT FK_ConversationParticipants_Conversations FOREIGN KEY (ConversationId) REFERENCES dbo.Conversations(ConversationId),
        CONSTRAINT FK_ConversationParticipants_Users FOREIGN KEY (UserId) REFERENCES dbo.Users(UserId)
    );
END
GO

/* Chat-ի հաղորդագրություններ */
IF OBJECT_ID(N'dbo.Messages', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.Messages (
        MessageId INT IDENTITY(1,1) PRIMARY KEY,
        ConversationId INT NOT NULL,
        SenderId INT NOT NULL,
        Body NVARCHAR(MAX) NOT NULL,
        CreatedAt DATETIME2 NOT NULL CONSTRAINT DF_Messages_CreatedAt DEFAULT SYSUTCDATETIME(),
        IsRead BIT NOT NULL CONSTRAINT DF_Messages_IsRead DEFAULT 0,
        CONSTRAINT FK_Messages_Conversations FOREIGN KEY (ConversationId) REFERENCES dbo.Conversations(ConversationId),
        CONSTRAINT FK_Messages_Senders FOREIGN KEY (SenderId) REFERENCES dbo.Users(UserId)
    );
END
GO

/* Արագ որոնման index-ներ */
IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Users_Username' AND object_id = OBJECT_ID(N'dbo.Users'))
    CREATE INDEX IX_Users_Username ON dbo.Users(Username);
GO

IF NOT EXISTS (SELECT 1 FROM sys.indexes WHERE name = N'IX_Messages_Conversation_CreatedAt' AND object_id = OBJECT_ID(N'dbo.Messages'))
    CREATE INDEX IX_Messages_Conversation_CreatedAt ON dbo.Messages(ConversationId, CreatedAt);
GO
