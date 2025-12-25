# How-to: LINEコンテンツの手動ダウンロードガイド

このガイドは、LINEのスタンプや絵文字を種類別に手動でダウンロードし、コンテンツ本体のファイルを特定する方法をまとめたものです。

`{id}` の部分は、各コンテンツのプロダクトIDに置き換えてください。

## スタンプ (Stickers)

| 種類 | ダウンロードURL | コンテンツのパス |
| :--- | :--- | :--- |
| **普通のスタンプ** | `http://dl.stickershop.line.naver.jp/products/0/0/1/{id}/iphone/stickers@2x.zip` | `/(数字)@2x.png` |
| **メッセージスタンプ** | `https://stickershop.line-scdn.net/stickershop/v1/product/{id}/iphone/sticker_name_base@2x.zip` | `/(数字)@2x.png` |
| **動くスタンプ** | `http://dl.stickershop.line.naver.jp/products/0/0/1/{id}/iphone/stickerpack@2x.zip` | `/animation@2x/(数字)@2x.png` |
| **エフェクトスタンプ**| `http://dl.stickershop.line.naver.jp/products/0/0/1/{id}/iphone/stickerpack@2x.zip` | `/(数字)@2x.png`<br>`/popup/(数字).png` |

## 絵文字 (Emojis)

| 種類 | ダウンロードURL | コンテンツのパス |
| :--- | :--- | :--- |
| **普通の絵文字** | `http://dl.stickershop.line.naver.jp/sticonshop/v1/{id}/sticon/iphone/package.zip?v=1` | `/(数字).png` |
| **動く/音あり絵文字** | `https://stickershop.line-scdn.net/sticonshop/v1/{id}/sticon/iphone/package_animation.zip` | `/(数字)_animation.png` |

---

### ファイルの整理について

上記の**コンテンツのパス**に該当しないファイル（例: `_key.png` がつくファイル、`productInfo.meta`、`meta.json`など）は、サムネイル画像やメタデータです。