using MediatR;
using Microsoft.AspNetCore.Mvc;
using TT99.APPL.Features.Items;
using System.Threading.Tasks;

namespace TT99.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ItemController : ControllerBase
    {
        private readonly IMediator _mediator;

        public ItemController(IMediator mediator)
        {
            _mediator = mediator;
        }

        /// <summary>
        /// Tạo một Item mới.
        /// </summary>
        /// <param name="command">Dữ liệu Command để tạo Item.</param>
        /// <returns>ID của Item vừa tạo.</returns>
        [HttpPost]
        public async Task<IActionResult> Create([FromBody] CreateItemCommand command)
        {
            // 1. Khi Send() được gọi, MediatR Pipeline sẽ khởi động.
            // 2. ValidationBehavior (mà chúng ta đã đăng ký) sẽ chạy trước tiên.
            // 3. Nếu CreateItemCommandValidator tìm thấy lỗi, nó sẽ ném ValidationException.
            //    (Lưu ý: Bạn cần một Middleware để bắt ValidationException và trả về HTTP 400 Bad Request, 
            //    nhưng ở đây, chúng ta chỉ tập trung vào việc kích hoạt Validation).
            // 4. Nếu không có lỗi, Handler sẽ được gọi và trả về kết quả.

            var itemId = await _mediator.Send(command);

            return CreatedAtAction(nameof(GetItemById), new { id = itemId }, new { id = itemId });
        }
        
        // Endpoint giả định để hoàn thành CreatedAtAction
        [HttpGet("{id}")]
        public IActionResult GetItemById(string id)
        {
            return Ok(new { Id = id, Status = "Pending" });
        }
    }
}