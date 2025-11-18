using FluentValidation;

namespace TT99.APPL.Features.Items
{
    public class CreateItemCommandValidator : AbstractValidator<CreateItemCommand>
    {
        public CreateItemCommandValidator()
        {
            // Quy tắc 1: Trường Name không được rỗng hoặc null, và độ dài tối đa là 50 ký tự.
            RuleFor(x => x.Name)
                .NotEmpty().WithMessage("Tên mặt hàng không được để trống.")
                .MaximumLength(50).WithMessage("Tên không được vượt quá 50 ký tự.");

            // Quy tắc 2: Trường Price phải lớn hơn 0.
            RuleFor(x => x.Price)
                .GreaterThan(0).WithMessage("Giá phải là một số dương.");

            // Quy tắc 3: Trường Notes (Tùy chọn) chỉ cần kiểm tra độ dài tối đa.
            RuleFor(x => x.Notes)
                .MaximumLength(200).WithMessage("Ghi chú không được vượt quá 200 ký tự.");
        }
    }
}