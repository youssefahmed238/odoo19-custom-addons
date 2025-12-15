/** @odoo-module **/

import {useService} from "@web/core/utils/hooks";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";
import {registry} from "@web/core/registry";
import {FileUploader} from "@web/views/fields/file_handler";

import {Component} from "@odoo/owl";

export class DXFFileUploader extends Component {
    static template = "product.DXFFileUploader";
    static props = {
        ...standardWidgetProps,
    };
    static components = {FileUploader};

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
    }

    async onFileUploaded(file) {
        if (!file || !file.data) {
            this.notification.add("Failed to upload DXF file.", {
                type: "danger",
            });
            return;
        }

        try {
            const fileName = file.name.replace(".dxf", "");

           const shape = await this.orm.call(
                "product.template",
                "convert_dxf_to_image1920",
                [[this.props.record.id], file.data],
                {}
            );

            this.props.record.update({
                name: fileName,
                dxf_file: file.data,
                width: shape['width'],
                height: shape['height'],
                shape_points: shape['shape_points'],
                image_1920: shape['image'],
                type: 'service',
            });

            this.notification.add(`DXF file "${fileName}" uploaded and converted successfully.`, {
                type: "success",
            });
        } catch (error) {
            console.error("DXF Upload - Error:", error);
            this.notification.add(`Error processing DXF file: ${error.message}`, {
                type: "danger",
            });
        }
    }
}

export const dxfFileUploader = {
    component: DXFFileUploader,
};

registry.category("view_widgets").add("dxf_file_uploader", dxfFileUploader);