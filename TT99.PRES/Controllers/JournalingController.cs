using MediatR;
using Microsoft.AspNetCore.Mvc;
using TT99.APPL.Cmmds;
using TT99.APPL.Qries;

namespace TT99.PRES.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class JournalingController : ControllerBase
    {
        // MediatR sẽ được Inject tự động nhờ DI
        private readonly IMediator _mediator;

        public JournalingController(IMediator mediator)
        {
            _mediator = mediator;
        }

        /// <summary>
        /// POST: Tạo và Ghi sổ một Bút toán mới (Command).
        /// </summary>
        /// <param name="command">Dữ liệu bút toán.</param>
        /// <returns>ID của bút toán đã được tạo.</returns>
        [HttpPost("create-entry")]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> CreateEntry([FromBody] CreateJournalEntryCommand command)
        {
            try
            {
                // MediatR sẽ tìm CreateJournalEntryHandler và thực thi nó
                var entryId = await _mediator.Send(command);
                return CreatedAtAction(nameof(GetEntry), new { id = entryId }, entryId);
            }
            catch (Exception ex)
            {
                // Xử lý các lỗi nghiệp vụ từ Domain/Application Layer
                return BadRequest(new { Error = "Lỗi nghiệp vụ khi ghi sổ", Message = ex.Message });
            }
        }
        
        // Phương thức tham khảo (chưa triển khai trong Handler)
        [HttpGet("{id}")]
        public IActionResult GetEntry(Guid id)
        {
            return Ok($"Chức năng tìm kiếm bút toán ID: {id} sẽ được triển khai sau.");
        }


        /// <summary>
        /// GET: Lấy báo cáo Sổ Cái (Query).
        /// </summary>
        /// <param name="query">Các tham số truy vấn báo cáo.</param>
        /// <returns>Danh sách các dòng DTO Sổ Cái.</returns>
        [HttpGet("ledger")]
        [ProducesResponseType(StatusCodes.Status200OK, Type = typeof(List<GeneralLedgerDto>))]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> GetGeneralLedger([FromQuery] GetGeneralLedgerQuery query)
        {
            try
            {
                // MediatR sẽ tìm GetGeneralLedgerHandler và thực thi nó
                var ledgerData = await _mediator.Send(query);
                return Ok(ledgerData);
            }
            catch (Exception ex)
            {
                 // Xử lý lỗi truy vấn (ví dụ: ngày không hợp lệ)
                return BadRequest(new { Error = "Lỗi truy vấn báo cáo", Message = ex.Message });
            }
        }
    }
}