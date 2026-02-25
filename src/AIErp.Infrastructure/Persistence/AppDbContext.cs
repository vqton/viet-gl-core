using AIErp.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace AIErp.Infrastructure.Persistence;

public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<Account> Accounts => Set<Account>();
    public DbSet<JournalEntry> JournalEntries => Set<JournalEntry>();
    public DbSet<JournalItem> JournalItems => Set<JournalItem>();
    public DbSet<Partner> Partners => Set<Partner>();
    public DbSet<FiscalPeriod> FiscalPeriods => Set<FiscalPeriod>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // Account configuration
        modelBuilder.Entity<Account>(entity =>
        {
            entity.ToTable("Accounts");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Code).IsRequired().HasMaxLength(20);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Type).IsRequired();
            entity.Property(e => e.NormalBalance).IsRequired();
            entity.Property(e => e.IsDetail).IsRequired();
            entity.Property(e => e.IsActive).IsRequired().HasDefaultValue(true);
            entity.Property(e => e.Description).HasMaxLength(500);
            
            // Audit fields
            entity.Property(e => e.CreatedBy).IsRequired().HasMaxLength(50);
            entity.Property(e => e.LastModifiedBy).IsRequired().HasMaxLength(50);
            
            // Self-referencing for hierarchy
            entity.HasOne(e => e.Parent)
                .WithMany(e => e.Children)
                .HasForeignKey(e => e.ParentId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => e.Code).IsUnique();
        });

        // JournalEntry configuration
        modelBuilder.Entity<JournalEntry>(entity =>
        {
            entity.ToTable("JournalEntries");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.EntryNumber).IsRequired().HasMaxLength(20);
            entity.Property(e => e.EntryDate).IsRequired();
            entity.Property(e => e.Currency).IsRequired().HasMaxLength(3).HasDefaultValue("VND");
            entity.Property(e => e.ExchangeRate).IsRequired().HasPrecision(18, 6).HasDefaultValue(1.0m);
            entity.Property(e => e.Description).IsRequired().HasMaxLength(500);
            entity.Property(e => e.Status).IsRequired();
            entity.Property(e => e.TotalDebit).IsRequired().HasPrecision(20, 4).HasDefaultValue(0m);
            entity.Property(e => e.TotalCredit).IsRequired().HasPrecision(20, 4).HasDefaultValue(0m);
            
            // Audit fields
            entity.Property(e => e.CreatedBy).IsRequired().HasMaxLength(50);
            entity.Property(e => e.LastModifiedBy).IsRequired().HasMaxLength(50);
            entity.Property(e => e.PostedBy).HasMaxLength(50);
            entity.Property(e => e.VoidedBy).HasMaxLength(50);
            
            // Relationships
            entity.HasOne(e => e.FiscalPeriod)
                .WithMany()
                .HasForeignKey(e => e.FiscalPeriodId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasIndex(e => e.EntryNumber).IsUnique();
            entity.HasIndex(e => e.EntryDate);
            entity.HasIndex(e => e.FiscalPeriodId);
            entity.HasIndex(e => e.Status);
        });

        // JournalItem configuration
        modelBuilder.Entity<JournalItem>(entity =>
        {
            entity.ToTable("JournalItems");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.DebitAmount).IsRequired().HasPrecision(20, 4).HasDefaultValue(0m);
            entity.Property(e => e.CreditAmount).IsRequired().HasPrecision(20, 4).HasDefaultValue(0m);
            entity.Property(e => e.BaseAmount).IsRequired().HasPrecision(20, 4).HasDefaultValue(0m);
            entity.Property(e => e.ExchangeRate).IsRequired().HasPrecision(18, 6).HasDefaultValue(1.0m);
            entity.Property(e => e.Description).HasMaxLength(250);
            
            // Audit fields
            entity.Property(e => e.CreatedBy).IsRequired().HasMaxLength(50);
            entity.Property(e => e.LastModifiedBy).IsRequired().HasMaxLength(50);
            
            // Relationships
            entity.HasOne(e => e.JournalEntry)
                .WithMany(e => e.Items)
                .HasForeignKey(e => e.JournalEntryId)
                .OnDelete(DeleteBehavior.Cascade);
            
            entity.HasOne(e => e.Account)
                .WithMany()
                .HasForeignKey(e => e.AccountId)
                .OnDelete(DeleteBehavior.Restrict);
            
            entity.HasOne(e => e.Partner)
                .WithMany()
                .HasForeignKey(e => e.PartnerId)
                .OnDelete(DeleteBehavior.SetNull);
            
            entity.HasIndex(e => e.JournalEntryId);
            entity.HasIndex(e => e.AccountId);
            entity.HasIndex(e => e.PartnerId);
        });

        // Partner configuration
        modelBuilder.Entity<Partner>(entity =>
        {
            entity.ToTable("Partners");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Code).IsRequired().HasMaxLength(20);
            entity.Property(e => e.Name).IsRequired().HasMaxLength(200);
            entity.Property(e => e.Type).IsRequired();
            entity.Property(e => e.TaxCode).HasMaxLength(20);
            entity.Property(e => e.Phone).HasMaxLength(20);
            entity.Property(e => e.Email).HasMaxLength(100);
            entity.Property(e => e.Address).HasMaxLength(500);
            entity.Property(e => e.IsActive).IsRequired().HasDefaultValue(true);
            entity.Property(e => e.IsSystem).IsRequired().HasDefaultValue(false);
            
            // Audit fields
            entity.Property(e => e.CreatedBy).IsRequired().HasMaxLength(50);
            entity.Property(e => e.LastModifiedBy).IsRequired().HasMaxLength(50);
            
            entity.HasIndex(e => e.Code).IsUnique();
            entity.HasIndex(e => e.Type);
        });

        // FiscalPeriod configuration
        modelBuilder.Entity<FiscalPeriod>(entity =>
        {
            entity.ToTable("FiscalPeriods");
            entity.HasKey(e => e.Id);
            entity.Property(e => e.Year).IsRequired();
            entity.Property(e => e.Period).IsRequired();
            entity.Property(e => e.StartDate).IsRequired();
            entity.Property(e => e.EndDate).IsRequired();
            entity.Property(e => e.IsOpen).IsRequired().HasDefaultValue(false);
            entity.Property(e => e.IsAdjustmentPeriod).IsRequired().HasDefaultValue(false);
            entity.Property(e => e.Description).HasMaxLength(200);
            
            // Audit fields
            entity.Property(e => e.CreatedBy).IsRequired().HasMaxLength(50);
            entity.Property(e => e.LastModifiedBy).IsRequired().HasMaxLength(50);
            
            entity.HasIndex(e => new { e.Year, e.Period }).IsUnique();
            entity.HasIndex(e => e.IsOpen);
        });
    }
}
