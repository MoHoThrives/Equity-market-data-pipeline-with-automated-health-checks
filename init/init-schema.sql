IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'MarketData')
BEGIN
    CREATE DATABASE MarketData;
END
GO

USE MarketData;
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'securities')
BEGIN
    CREATE TABLE securities (
        security_id INT IDENTITY PRIMARY KEY,
        ticker      NVARCHAR(10) NOT NULL UNIQUE,
        name        NVARCHAR(200) NOT NULL,
        sector      NVARCHAR(100) NULL
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'prices')
BEGIN
    CREATE TABLE prices (
        price_id           INT IDENTITY PRIMARY KEY,
        security_id        INT NOT NULL REFERENCES securities(security_id),
        trade_date          DATE NOT NULL,
        open_price          DECIMAL(18,4) NOT NULL,
        high_price          DECIMAL(18,4) NOT NULL,
        low_price           DECIMAL(18,4) NOT NULL,
        close_price         DECIMAL(18,4) NOT NULL,
        volume              BIGINT NOT NULL,
        daily_return        DECIMAL(18,6) NULL,
        moving_avg_50d       DECIMAL(18,4) NULL,
        rolling_volatility  DECIMAL(18,6) NULL,
        CONSTRAINT UQ_prices_security_date UNIQUE (security_id, trade_date)
    );

    CREATE INDEX IX_prices_trade_date ON prices(trade_date);
END
GO