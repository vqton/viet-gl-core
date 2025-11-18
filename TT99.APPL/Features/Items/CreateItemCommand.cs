using MediatR;
using System;

namespace TT99.APPL.Features.Items
{
    // Command là DTO (Data Transfer Object) chứa dữ liệu đầu vào
    // IRequest<T> định nghĩa kiểu dữ liệu trả về của Command (ở đây là một chuỗi ID)
    public class CreateItemCommand : IRequest<string>
    {
        // Yêu cầu (Required): Tên của Item
        public string Name { get; set; } = string.Empty;

        // Yêu cầu (Required): Giá trị phải lớn hơn 0
        public decimal Price { get; set; }

        // Tùy chọn: Ghi chú, không cần validate đặc biệt
        public string Notes { get; set; } = string.Empty;
    }
}