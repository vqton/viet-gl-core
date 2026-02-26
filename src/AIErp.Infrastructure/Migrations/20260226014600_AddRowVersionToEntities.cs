using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AIErp.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddRowVersionToEntities : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropIndex(
                name: "IX_Partners_Type",
                table: "Partners");

            migrationBuilder.AddColumn<Guid>(
                name: "RowVersion",
                table: "Partners",
                type: "TEXT",
                rowVersion: true,
                nullable: false,
                defaultValue: new Guid("00000000-0000-0000-0000-000000000000"));

            migrationBuilder.AddColumn<Guid>(
                name: "RowVersion",
                table: "JournalEntries",
                type: "TEXT",
                rowVersion: true,
                nullable: false,
                defaultValue: new Guid("00000000-0000-0000-0000-000000000000"));

            migrationBuilder.AddColumn<Guid>(
                name: "RowVersion",
                table: "FiscalPeriods",
                type: "TEXT",
                rowVersion: true,
                nullable: false,
                defaultValue: new Guid("00000000-0000-0000-0000-000000000000"));

            migrationBuilder.AddColumn<Guid>(
                name: "RowVersion",
                table: "Accounts",
                type: "TEXT",
                rowVersion: true,
                nullable: false,
                defaultValue: new Guid("00000000-0000-0000-0000-000000000000"));
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "RowVersion",
                table: "Partners");

            migrationBuilder.DropColumn(
                name: "RowVersion",
                table: "JournalEntries");

            migrationBuilder.DropColumn(
                name: "RowVersion",
                table: "FiscalPeriods");

            migrationBuilder.DropColumn(
                name: "RowVersion",
                table: "Accounts");

            migrationBuilder.CreateIndex(
                name: "IX_Partners_Type",
                table: "Partners",
                column: "Type");
        }
    }
}
