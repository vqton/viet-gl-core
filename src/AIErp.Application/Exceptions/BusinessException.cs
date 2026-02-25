namespace AIErp.Application.Exceptions;

public class BusinessException : Exception
{
    public string ErrorCode { get; }

    public BusinessException(string errorCode, string message) 
        : base(message)
    {
        ErrorCode = errorCode;
    }
}

public static class BusinessErrors
{
    public const string ImbalanceDetected = "IMBALANCE_DETECTED";
    public const string FiscalPeriodClosed = "FISCAL_PERIOD_CLOSED";
    public const string InvalidStatusTransition = "INVALID_STATUS_TRANSITION";
    public const string UnknownAccount = "UNKNOWN_ACCOUNT";
    public const string PartnerRequired = "PARTNER_REQUIRED";
    public const string ValidationError = "VALIDATION_ERROR";
    public const string NotFound = "NOT_FOUND";
}
