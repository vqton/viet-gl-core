using FluentValidation;
using System;

namespace TT99.APPL.Qries
{
    /// <summary>
    /// Validator cho Query GetGeneralLedgerQuery, sử dụng FluentValidation.
    /// Đảm bảo các tham số truy vấn (đặc biệt là ngày tháng) là hợp lệ.
    /// </summary>
    public class GetGeneralLedgerQueryValidator : AbstractValidator<GetGeneralLedgerQuery>
    {
        public GetGeneralLedgerQueryValidator()
        {
            // 1. StartDate không được trống
            RuleFor(q => q.StartDate)
                .NotEmpty().WithMessage("Ngày bắt đầu (StartDate) không được để trống.");

            // 2. EndDate không được trống
            RuleFor(q => q.EndDate)
                .NotEmpty().WithMessage("Ngày kết thúc (EndDate) không được để trống.");

            // 3. StartDate phải nhỏ hơn hoặc bằng EndDate
            RuleFor(q => q.StartDate)
                .LessThanOrEqualTo(q => q.EndDate)
                .WithMessage("Ngày bắt đầu phải nhỏ hơn hoặc bằng Ngày kết thúc.");

            // 4. EndDate không được ở tương lai (để đảm bảo báo cáo chỉ dùng dữ liệu đã phát sinh)
            RuleFor(q => q.EndDate.Date)
                .LessThanOrEqualTo(DateTime.Today.Date)
                .WithMessage("Ngày kết thúc không được vượt quá ngày hiện tại.");
        }
    }
}