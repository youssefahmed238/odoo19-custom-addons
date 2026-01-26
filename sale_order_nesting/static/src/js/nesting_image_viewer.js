/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { Component, onWillStart, useState, onWillUpdateProps } from "@odoo/owl";

class NestingImageViewer extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            sheets: [],
            loading: true,
        });

        onWillStart(() => this._loadImages());
        onWillUpdateProps(() => this._loadImages());
    }

    async _loadImages() {
        this.state.loading = true;
        this.state.sheets = [];

        const resId = this.props.record.resId;
        if (!resId) {
            this.state.loading = false;
            return;
        }

        const attachments = await this.orm.searchRead(
            "ir.attachment",
            [
                ["res_model", "=", "sale.order"],
                ["res_id", "=", resId],
                ["name", "ilike", "Nesting Result:"],
            ],
            ["id", "name", "description"]
        );

        // ---- GROUP BY SHEET NAME ----
        const grouped = {};

        for (const att of attachments) {
            const sheetName = att.name.replace("Nesting Result:", "").trim();

            if (!grouped[sheetName]) {
                grouped[sheetName] = {
                    name: sheetName,
                    images: [],
                };
            }

            grouped[sheetName].images.push({
                id: att.id,
                url: `/web/image/${att.id}`,
            });
        }

        this.state.sheets = Object.values(grouped).reverse();
        this.state.loading = false;
    }
}

NestingImageViewer.template = "nesting_image_viewer.Template";

registry.category("fields").add("nesting_image_viewer", {
    component: NestingImageViewer,
});
