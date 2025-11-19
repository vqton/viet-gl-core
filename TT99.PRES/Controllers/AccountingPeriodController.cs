// File: D:\tt99acct\TT99.PRES\Controllers\AccountingPeriodController.cs
using MediatR;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Threading.Tasks;
using TT99.APPL.Cmmds;

namespace TT99.PRES.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AccountingPeriodController : ControllerBase
    {
        private readonly IMediator _mediator;

        public AccountingPeriodController(IMediator mediator)
        {
            _mediator = mediator;
        }

        /// <summary>
        /// POST: Tạo một kỳ kế toán mới.
        /// </summary>
        /// <param name="command">Dữ liệu kỳ kế toán.</param>
        /// <returns>ID của kỳ kế toán vừa tạo.</returns>
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> CreatePeriod([FromBody] CreateAccountingPeriodCommand command)
        {
            try
            {
                var periodId = await _mediator.Send(command);
                return CreatedAtAction(nameof(GetPeriodById), new { id = periodId }, periodId); // Trả về ID và đường dẫn đến kỳ vừa tạo
            }
            catch (Exception ex)
            {
                // Ghi log lỗi nếu cần
                return BadRequest(new { Error = "Lỗi khi tạo kỳ kế toán", Message = ex.Message });
            }
        }

        /// <summary>
        /// POST: Khóa một kỳ kế toán.
        /// </summary>
        /// <param name="command">Dữ liệu yêu cầu khóa kỳ (ID).</param>
        /// <returns>200 OK nếu thành công.</returns>
        [HttpPost("lock")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> LockPeriod([FromBody] LockPeriodCommand command)
        {
            try
            {
                await _mediator.Send(command);
                return Ok(new { Message = "Kỳ kế toán đã được khóa thành công." });
            }
            catch (Exception ex)
            {
                // Ghi log lỗi nếu cần
                return BadRequest(new { Error = "Lỗi khi khóa kỳ kế toán", Message = ex.Message });
            }
        }

        /// <summary>
        /// POST: Mở một kỳ kế toán đã bị khóa.
        /// </summary>
        /// <param name="command">Dữ liệu yêu cầu mở kỳ (ID).</param>
        /// <returns>200 OK nếu thành công.</returns>
        [HttpPost("unlock")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<IActionResult> UnlockPeriod([FromBody] UnlockPeriodCommand command)
        {
            try
            {
                await _mediator.Send(command);
                return Ok(new { Message = "Kỳ kế toán đã được mở khóa thành công." });
            }
            catch (Exception ex)
            {
                // Ghi log lỗi nếu cần
                return BadRequest(new { Error = "Lỗi khi mở khóa kỳ kế toán", Message = ex.Message });
            }
        }

        // Có thể thêm các endpoint GET để lấy danh sách, tìm theo ID, v.v. nếu cần sau.
        [HttpGet("{id}")]
        public IActionResult GetPeriodById(Guid id)
        {
             // TODO: Thêm Query và Handler để lấy thông tin kỳ theo ID
             return Ok($"Chức năng lấy kỳ theo ID: {id} sẽ được triển khai sau.");
        }
    }
}