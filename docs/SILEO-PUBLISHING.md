# TAstore Sileo — quy trình phát hành có kiểm soát

## Trạng thái hiện tại (2026-10-12)
- Website công khai: `https://tastore.app/`.
- Gian sản phẩm: `https://tastore.app/repo/` (HTML, **không phải** nguồn APT hoạt động).
- `TAstore-web/repo/` **chưa có** `Packages`, `Packages.gz`, `Release`, `pool/` đã xác nhận. Không công bố liên kết `sileo://` lúc này.
- Security5 của MultiTA RH15/RH16 và trial activation đang được kiểm thử bên ngoài repo web.
- Không tự sao chép gói CleanTA thử nghiệm cũ từ repo khác vào đây.

## Quy tắc cứng
1. Public repo chỉ chứa HTML/CSS, mô tả gói, DEB được chủ dự án chấp thuận phát hành và chỉ mục APT tương ứng. Không đưa source, broker secret, private key, .env, debug log, test key.
2. Trước khi upload một DEB: xác thực nguồn build, hash SHA256, Package, Version, Architecture, Depends/Conflicts, firmware bound, các script maintainer, path layout RootHide/rootless, entitlements, chữ ký/integrity và trạng thái kiểm thử iPhone.
3. MultiTA RH15: chỉ iOS 15 RootHide. RH16: chỉ iOS 16 RootHide. Không suy luận sự tương thích chỉ từ tên file.
4. RH15/RH16 không được cài song song với `com.sushibta.multita.beta`; kiểm tra luồng uninstall và dữ liệu license/config.
5. Khách chỉ được kích hoạt sau khi server xác minh license. Không đăng beta mới khi gate license chưa hoạt động hoặc bị bypass.
6. Dừng việc công bố nếu APT metadata trỏ tới file không có thật, checksum sai, thiếu phụ thuộc hoặc index có phiên bản nhầm.
7. Repo phát hành lâu dài nên có GPG release signing; checksum trong Release không thay thế chữ ký. Không bao giờ lưu private signing key trong GitHub.

## Các bước khi Claude bàn giao
1. Nhận RH15/RH16 release candidate kèm source, diff, kết quả test và hash; kiểm tra với bản nền 5j/5m.
2. Test trên iPhone RootHide iOS 15/16: install/update/uninstall, CarPlay, YouTube, split, Auto Split, license đúng/sai/hết hạn/offline và respring.
3. Kiểm tra và duyệt từng DEB. Chỉ chuyển những gói đạt test vào **bản sao làm việc** của `TAstore-web/repo/pool/`.
4. Sinh `Packages`, `Packages.gz`, `Release` từ DEB thật và ký repo nếu đã thiết lập signing. Không sao chép chỉ mục cũ của `TAstore` sang `TAstore-web`.
5. Chạy `python3 scripts/verify_sileo_repo.py` ở thư mục gốc `TAstore-web`; lỗi nào cũng phải sửa trước khi push.
6. Commit DEB cùng Packages/Packages.gz/Release trong cùng lần phát hành. Sau deploy, đối chiếu URL DEB và file index qua HTTPS với SHA256 bản local.
7. Chỉ khi nguồn APT được Sileo chấp nhận trên thiết bị mới mở nút "Thêm nguồn Sileo" và chương trình trải nghiệm.

## Phân công
- Claude: Security5/lease/broker, nghiệm thu chức năng và source DEB RH15/RH16.
- ChatGPT: website TAstore, repo APT, chỉ mục, xác minh đường dẫn và quy trình phát hành.
- Chủ dự án: phê duyệt DEB và thử nghiệm cuối trên iPhone.

Địa chỉ trang gian hàng `https://tastore.app/repo/` có thể khác URL nguồn APT thực tế. URL nguồn sẽ được xác định sau khi cấu trúc và triển khai APT hoạt động; không giả định `/repo/` đã là một nguồn cài được.
