@echo off
setlocal

set "ROOT=D:\tt99acct"

echo Creating project structure at %ROOT%...

:: Tạo thư mục gốc
mkdir "%ROOT%" 2>nul

:: docs
mkdir "%ROOT%\docs"
mkdir "%ROOT%\docs\requirements"
mkdir "%ROOT%\docs\architecture"
mkdir "%ROOT%\docs\legal"
mkdir "%ROOT%\docs\user_manual"

:: src/domain
mkdir "%ROOT%\src\domain"
mkdir "%ROOT%\src\domain\entities"
mkdir "%ROOT%\src\domain\value_objects"
mkdir "%ROOT%\src\domain\repositories"
mkdir "%ROOT%\src\domain\services"
mkdir "%ROOT%\src\domain\rules"

:: src/application
mkdir "%ROOT%\src\application"
mkdir "%ROOT%\src\application\use_cases"
mkdir "%ROOT%\src\application\dto"

:: src/interfaces
mkdir "%ROOT%\src\interfaces"
mkdir "%ROOT%\src\interfaces\ui"
mkdir "%ROOT%\src\interfaces\database"
mkdir "%ROOT%\src\interfaces\external"
mkdir "%ROOT%\src\interfaces\api"

:: src/config
mkdir "%ROOT%\src\config"

:: tests
mkdir "%ROOT%\tests"
mkdir "%ROOT%\tests\unit"
mkdir "%ROOT%\tests\integration"
mkdir "%ROOT%\tests\compliance"

:: scripts
mkdir "%ROOT%\scripts"

:: Tạo file placeholder
type nul > "%ROOT%\docs\requirements\ur.md"
type nul > "%ROOT%\docs\requirements\srs.md"
type nul > "%ROOT%\docs\architecture\system_architecture.md"
type nul > "%ROOT%\docs\architecture\erd.md"
type nul > "%ROOT%\docs\legal\tt99_references.md"
type nul > "%ROOT%\docs\user_manual\user_guide.md"

type nul > "%ROOT%\src\domain\entities\Account.py"
type nul > "%ROOT%\src\domain\entities\Document.py"
type nul > "%ROOT%\src\domain\entities\InventoryItem.py"
type nul > "%ROOT%\src\domain\entities\JournalEntry.py"
type nul > "%ROOT%\src\domain\entities\FinancialReport.py"

type nul > "%ROOT%\src\domain\value_objects\Money.py"
type nul > "%ROOT%\src\domain\value_objects\TaxCode.py"
type nul > "%ROOT%\src\domain\value_objects\AccountingPeriod.py"

type nul > "%ROOT%\src\domain\repositories\IAccountRepository.py"
type nul > "%ROOT%\src\domain\repositories\IDocumentRepository.py"
type nul > "%ROOT%\src\domain\repositories\IReportingRepository.py"

type nul > "%ROOT%\src\domain\services\AccountingRuleEngine.py"
type nul > "%ROOT%\src\domain\services\InventoryValuationService.py"
type nul > "%ROOT%\src\domain\services\TaxCalculationService.py"
type nul > "%ROOT%\src\domain\services\FinancialReportingService.py"

type nul > "%ROOT%\src\domain\rules\PurchaseAccountingRule.py"
type nul > "%ROOT%\src\domain\rules\SalesAccountingRule.py"
type nul > "%ROOT%\src\domain\rules\InventoryAdjustmentRule.py"

:: Tạo file coa_99.json mẫu (trống, sẽ điền sau)
type nul > "%ROOT%\src\domain\rules\coa_99.json"

:: application
type nul > "%ROOT%\src\application\use_cases\RecordPurchaseUseCase.py"
type nul > "%ROOT%\src\application\use_cases\RecordSalesUseCase.py"
type nul > "%ROOT%\src\application\use_cases\GenerateFinancialReportUseCase.py"
type nul > "%ROOT%\src\application\use_cases\CloseAccountingPeriodUseCase.py"

type nul > "%ROOT%\src\application\dto\PurchaseDTO.py"
type nul > "%ROOT%\src\application\dto\SalesDTO.py"

:: interfaces
type nul > "%ROOT%\src\interfaces\ui\placeholder.txt"
type nul > "%ROOT%\src\interfaces\database\placeholder.txt"
type nul > "%ROOT%\src\interfaces\external\EInvoiceGateway.py"
type nul > "%ROOT%\src\interfaces\external\TaxSubmissionGateway.py"
type nul > "%ROOT%\src\interfaces\api\placeholder.txt"

:: config
type nul > "%ROOT%\src\config\container.py"

:: tests
type nul > "%ROOT%\tests\unit\placeholder.txt"
type nul > "%ROOT%\tests\integration\placeholder.txt"
type nul > "%ROOT%\tests\compliance\placeholder.txt"

:: scripts
type nul > "%ROOT%\scripts\import_initial_balance.py"
type nul > "%ROOT%\scripts\export_tax_xml.py"

:: root files
type nul > "%ROOT%\.gitignore"
type nul > "%ROOT%\README.md"
type nul > "%ROOT%\requirements.txt"

echo.
echo ✅ Project structure created successfully at %ROOT%
echo You can now start implementing in src\domain\
pause