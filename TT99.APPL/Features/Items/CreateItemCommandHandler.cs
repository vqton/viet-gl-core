using MediatR;
using System;
using System.Threading;
using System.Threading.Tasks;

namespace TT99.APPL.Features.Items
{
    public class CreateItemCommandHandler : IRequestHandler<CreateItemCommand, string>
    {
        // Giả lập một dịch vụ (ví dụ: DbContext, Repository) để lưu dữ liệu
        // private readonly IItemRepository _itemRepository;

        // public CreateItemCommandHandler(IItemRepository itemRepository)
        // {
        //     _itemRepository = itemRepository;
        // }

        public async Task<string> Handle(CreateItemCommand request, CancellationToken cancellationToken)
        {
            // LƯU Ý QUAN TRỌNG:
            // Nếu ValidationBehavior hoạt động đúng, code trong Handler này
            // CHỈ chạy khi dữ liệu đầu vào (request) là HỢP LỆ.

            // 1. Logic ánh xạ DTO sang Entity:
            // var itemEntity = new Item(request.Name, request.Price, request.Notes);

            // 2. Logic lưu vào Database (Giả lập):
            // await _itemRepository.AddAsync(itemEntity);

            // Tạo một ID giả định và trả về
            var newId = Guid.NewGuid().ToString();

            Console.WriteLine($"[HANDLER LOG] Item '{request.Name}' với giá {request.Price:C} đã được tạo thành công. ID: {newId}");
            
            // Trả về ID của Item vừa tạo
            return await Task.FromResult(newId);
        }
    }
}