// File: D:\tt99acct\TT99.PRES\Controllers\AccountController.cs
using MediatR;
using Microsoft.AspNetCore.Mvc;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using TT99.APPL.Cmmds; // hoặc Qries nếu có
using TT99.DMN.Ents;

namespace TT99.PRES.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AccountController : ControllerBase
    {
        private readonly IMediator _mediator;

        public AccountController(IMediator mediator)
        {
            _mediator = mediator;
        }

        // GET: api/Account
        [HttpGet]
        public async Task<ActionResult<List<Account>>> GetAllAccounts()
        {
            // TODO: Gọi Query để lấy tất cả tài khoản
            // var query = new GetAllAccountsQuery();
            // var accounts = await _mediator.Send(query);
            // return Ok(accounts);

            // Tạm thời: Trả về danh sách rỗng hoặc lấy từ DB trực tiếp nếu chưa có Query
            // return Ok(new List<Account>());
            // Ví dụ giả lập:
            return Ok(new List<Account> { new Account("111", "Tiền mặt", AccountType.Asset) }); // Thay bằng logic thực tế
        }

        // GET: api/Account/5
        [HttpGet("{id}")]
        public async Task<ActionResult<Account>> GetAccountById(string id) // ID là AccountNumber
        {
            // TODO: Gọi Query để lấy tài khoản theo ID
            // var query = new GetAccountByIdQuery { AccountNumber = id };
            // var account = await _mediator.Send(query);
            // if (account == null) return NotFound();

            // return Ok(account);

            // Tạm thời: Trả về một tài khoản giả lập nếu ID khớp
            if (id == "111")
            {
                return Ok(new Account("111", "Tiền mặt", AccountType.Asset));
            }
            return NotFound();
        }

        // POST: api/Account
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<string>> CreateAccount([FromBody] CreateAccountCommand command) // Thay CreateAccountCommand bằng Command thực tế
        {
            try
            {
                // var accountNumber = await _mediator.Send(command);
                // return CreatedAtAction(nameof(GetAccountById), new { id = accountNumber }, accountNumber);

                // Tạm thời: Giả lập tạo tài khoản
                var newAccount = new Account(command.AccountNumber, command.AccountName, command.Type, command.Level, command.ParentAccountNumber);
                // Gọi service hoặc repository để thêm vào DB
                // await _accountRepository.AddAsync(newAccount);
                // await _context.SaveChangesAsync(); // Nếu dùng DbContext trực tiếp trong Controller (không khuyến khích nếu dùng Application Service)

                return CreatedAtAction(nameof(GetAccountById), new { id = newAccount.AccountNumber }, newAccount.AccountNumber);
            }
            catch (Exception ex)
            {
                // Ghi log lỗi nếu cần
                return BadRequest(new { Error = "Lỗi khi tạo tài khoản", Message = ex.Message });
            }
        }

        // PUT: api/Account/5
        [HttpPut("{id}")] // ID là AccountNumber
        public async Task<IActionResult> UpdateAccount(string id, [FromBody] UpdateAccountCommand command) // Thay UpdateAccountCommand bằng Command thực tế
        {
            if (id != command.AccountNumber)
            {
                return BadRequest("ID trong URL không khớp với ID trong body.");
            }

            try
            {
                // await _mediator.Send(command);
                // return NoContent();

                // Tạm thời: Giả lập cập nhật
                // var account = await _accountRepository.GetByIdAsync(id);
                // if (account == null) return NotFound();

                // account.Update(command.NewName, command.NewType, ...); // Gọi phương thức trong Entity nếu có
                // await _accountRepository.UpdateAsync(account);
                // await _context.SaveChangesAsync();

                return NoContent();
            }
            catch (Exception ex)
            {
                // Ghi log lỗi nếu cần
                return BadRequest(new { Error = "Lỗi khi cập nhật tài khoản", Message = ex.Message });
            }
        }

        // DELETE: api/Account/5
        [HttpDelete("{id}")] // ID là AccountNumber
        public async Task<IActionResult> DeleteAccount(string id)
        {
            try
            {
                // var command = new DeleteAccountCommand { AccountNumber = id };
                // await _mediator.Send(command);
                // return NoContent();

                // Tạm thời: Giả lập xóa
                // var account = await _accountRepository.GetByIdAsync(id);
                // if (account == null) return NotFound();

                // await _accountRepository.RemoveAsync(account);
                // await _context.SaveChangesAsync();

                return NoContent();
            }
            catch (Exception ex)
            {
                // Ghi log lỗi nếu cần
                return BadRequest(new { Error = "Lỗi khi xóa tài khoản", Message = ex.Message });
            }
        }
    }
}