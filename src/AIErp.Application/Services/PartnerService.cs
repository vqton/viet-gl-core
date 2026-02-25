namespace AIErp.Application.Services;

using AIErp.Application.DTOs;
using AIErp.Application.Exceptions;
using AIErp.Application.Interfaces;
using AIErp.Domain.Entities;
using AIErp.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

public class PartnerService(AppDbContext dbContext) : IPartnerService
{
    private readonly AppDbContext _dbContext = dbContext;

    public async Task<IEnumerable<PartnerDto>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        var partners = await _dbContext.Partners
            .OrderBy(p => p.Code)
            .ToListAsync(cancellationToken);

        return partners.Select(MapToDto);
    }

    public async Task<PartnerDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var partner = await _dbContext.Partners
            .FirstOrDefaultAsync(p => p.Id == id, cancellationToken);

        return partner == null ? null : MapToDto(partner);
    }

    public async Task<PartnerDto> CreateAsync(CreatePartnerDto dto, string createdBy, CancellationToken cancellationToken = default)
    {
        var exists = await _dbContext.Partners
            .AnyAsync(p => p.Code == dto.Code, cancellationToken);

        if (exists)
            throw new BusinessException(BusinessErrors.ValidationError, $"Partner code '{dto.Code}' already exists");

        var partner = Partner.Create(
            code: dto.Code,
            name: dto.Name,
            type: dto.Type,
            createdBy: createdBy,
            taxCode: dto.TaxCode,
            phone: dto.Phone,
            email: dto.Email,
            address: dto.Address
        );

        await _dbContext.Partners.AddAsync(partner, cancellationToken);
        await _dbContext.SaveChangesAsync(cancellationToken);

        return MapToDto(partner);
    }

    public async Task<PartnerDto> UpdateAsync(Guid id, UpdatePartnerDto dto, string modifiedBy, CancellationToken cancellationToken = default)
    {
        var partner = await _dbContext.Partners
            .FirstOrDefaultAsync(p => p.Id == id, cancellationToken)
            ?? throw new BusinessException(BusinessErrors.ValidationError, "Partner not found");

        partner.Update(
            name: dto.Name,
            type: dto.Type,
            modifiedBy: modifiedBy,
            taxCode: dto.TaxCode,
            phone: dto.Phone,
            email: dto.Email,
            address: dto.Address
        );

        await _dbContext.SaveChangesAsync(cancellationToken);

        return MapToDto(partner);
    }

    public async Task DeleteAsync(Guid id, string deletedBy, CancellationToken cancellationToken = default)
    {
        var partner = await _dbContext.Partners
            .FirstOrDefaultAsync(p => p.Id == id, cancellationToken)
            ?? throw new BusinessException(BusinessErrors.ValidationError, "Partner not found");

        partner.Deactivate(deletedBy);
        await _dbContext.SaveChangesAsync(cancellationToken);
    }

    private static PartnerDto MapToDto(Partner partner)
    {
        return new PartnerDto
        {
            Id = partner.Id,
            Code = partner.Code,
            Name = partner.Name,
            Type = partner.Type,
            TaxCode = partner.TaxCode,
            Phone = partner.Phone,
            Email = partner.Email,
            Address = partner.Address,
            IsActive = partner.IsActive,
            IsSystem = partner.IsSystem
        };
    }
}
