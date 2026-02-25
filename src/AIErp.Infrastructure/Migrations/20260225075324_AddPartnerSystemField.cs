using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace AIErp.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddPartnerSystemField : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<bool>(
                name: "IsSystem",
                table: "Partners",
                type: "INTEGER",
                nullable: false,
                defaultValue: false);
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropColumn(
                name: "IsSystem",
                table: "Partners");
        }
    }
}
