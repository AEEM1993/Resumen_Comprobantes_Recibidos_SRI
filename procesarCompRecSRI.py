import sys
import os
from xml.dom import minidom
import xmltodict
import json


def printArray(array):
    print("------------------------0------------------------")
    ith = 0
    for item in array:
        print(f'[{ith}]: {item}')
        ith += 1
    print("------------------------0------------------------")


def processXmlFile(folder, file):
    xml_file = minidom.parse(f'./{folder}/{file}')
    comprobante = xml_file.getElementsByTagName('comprobante')
    for elem in comprobante:
        print(f'File: {file}')
        comprobante_dict = xmltodict.parse(elem.firstChild.data)
        return comprobante_dict


def processFactura(comprobante):
    factura_dict = {
        "facturaNumero": comprobante["factura"]["infoTributaria"]["estab"] + "-" + comprobante["factura"]["infoTributaria"]["ptoEmi"] + "-" + comprobante["factura"]["infoTributaria"]["secuencial"],
        "razonSocial": comprobante["factura"]["infoTributaria"]["razonSocial"],
        "rucVendedor": comprobante["factura"]["infoTributaria"]["ruc"],
        "identificacionComprador": comprobante["factura"]["infoFactura"]["identificacionComprador"],
        "facturaFecha": comprobante["factura"]["infoFactura"]["fechaEmision"],
        "importeTotal": comprobante["factura"]["infoFactura"]["importeTotal"],
        "subtotal_0": "0.00",
        "IVA_0": "0.00",
        "subtotal_12": "0.00",
        "IVA_12": "0.00",
        "subtotal_15": "0.00",
        "IVA_15":"0.00",
        "propina": comprobante["factura"]["infoFactura"]["propina"] if ("propina" in comprobante["factura"]["infoFactura"].keys()) else 0,
        "otrosRubrosTercerosTotal": 0,
        "detalles": []
    }
    totalConImpuestos = comprobante["factura"]["infoFactura"]["totalConImpuestos"]["totalImpuesto"]
    # print(totalConImpuestos)
    if isinstance(totalConImpuestos, list):
        for totalImpuesto in totalConImpuestos:
            if totalImpuesto['codigoPorcentaje'] == '0':
                factura_dict["subtotal_0"] = totalImpuesto['baseImponible']
                factura_dict["IVA_0"] = totalImpuesto['valor']

            if totalImpuesto['codigoPorcentaje'] == '2':
                factura_dict["subtotal_12"] = totalImpuesto['baseImponible']
                factura_dict["IVA_12"] = totalImpuesto['valor']

            if totalImpuesto['codigoPorcentaje'] == '4':
                factura_dict["subtotal_15"] = totalImpuesto['baseImponible']
                factura_dict["IVA_15"] = totalImpuesto['valor']
            # print(totalImpuesto)
    else:
        totalImpuesto = totalConImpuestos
        if totalImpuesto['codigoPorcentaje'] == '0':
            factura_dict["subtotal_0"] = totalImpuesto['baseImponible']
            factura_dict["IVA_0"] = totalImpuesto['valor']

        if totalImpuesto['codigoPorcentaje'] == '2':
            factura_dict["subtotal_12"] = totalImpuesto['baseImponible']
            factura_dict["IVA_12"] = totalImpuesto['valor']
        
        if totalImpuesto['codigoPorcentaje'] == '4':
                factura_dict["subtotal_15"] = totalImpuesto['baseImponible']
                factura_dict["IVA_15"] = totalImpuesto['valor']

    total = round(float(factura_dict['subtotal_0']) + float(
        factura_dict['subtotal_12']) + float(factura_dict['IVA_12']) +
        float(factura_dict['subtotal_15']) + float(factura_dict['IVA_15'])  + float(factura_dict["propina"]), 2)
    
    diferenciaSignificativa = round(abs(total - float(factura_dict["importeTotal"])),2)
    
    if (diferenciaSignificativa > 0.01):
        print(diferenciaSignificativa)
        totalOtrosRubrosTerceros = 0
        otrosRubrosTerceros = comprobante["factura"]["otrosRubrosTerceros"]["rubro"]

        if isinstance(otrosRubrosTerceros, list):
            for rubro in otrosRubrosTerceros:
                totalOtrosRubrosTerceros += float(rubro["total"])
        else:
            rubro = otrosRubrosTerceros
            totalOtrosRubrosTerceros += float(rubro["total"])
        factura_dict["otrosRubrosTercerosTotal"] = totalOtrosRubrosTerceros
    elif (diferenciaSignificativa == 0.01):
        total = round(float(factura_dict["importeTotal"]))


    detalles = comprobante["factura"]["detalles"]["detalle"]
    # print(detalles)
    if isinstance(detalles, list):
        for detalle in detalles:
            factura_detalle = {
                "cantidad": detalle["cantidad"],
                "descripcion": detalle["descripcion"],
                "precioUnitario": detalle["precioUnitario"],
                "descuento": detalle["descuento"],
                "precioTotalSinImpuestos": detalle["precioTotalSinImpuesto"],
                "impuestos": detalle["impuestos"]

            }
            factura_dict["detalles"].append(factura_detalle)
    else:
        detalle = detalles
        factura_detalle = {
            "cantidad": detalle["cantidad"],
            "descripcion": detalle["descripcion"],
            "precioUnitario": detalle["precioUnitario"],
            "descuento": detalle["descuento"],
            "precioTotalSinImpuestos": detalle["precioTotalSinImpuesto"],
            "impuestos": detalle["impuestos"]

        }
        factura_dict["detalles"].append(factura_detalle)

    return factura_dict


def computeFacturas(facturas_array):
    resumen_dict = {
        "subtotal_0": 0,
        "subtotal_12": 0,
        "IVA_12": 0,
        "subtotal_15": 0,
        "IVA_15": 0,
        "propina_total": 0,
        "otros_rubros_total": 0,
        "importe_total": 0

    }
    for factura in facturas_array:
        resumen_dict["subtotal_0"] += float(factura["subtotal_0"])
        resumen_dict["subtotal_0"] = round(resumen_dict["subtotal_0"], 2)

        resumen_dict["subtotal_12"] += float(factura["subtotal_12"])
        resumen_dict["subtotal_12"] = round(resumen_dict["subtotal_12"], 2)

        resumen_dict["IVA_12"] += float(factura["IVA_12"])
        resumen_dict["IVA_12"] = round(resumen_dict["IVA_12"], 2)

        resumen_dict["subtotal_15"] += float(factura["subtotal_15"])
        resumen_dict["subtotal_15"] = round(resumen_dict["subtotal_15"], 2)

        resumen_dict["IVA_15"] += float(factura["IVA_15"])
        resumen_dict["IVA_15"] = round(resumen_dict["IVA_15"], 2)


        resumen_dict["importe_total"] += float(factura["importeTotal"])
        resumen_dict["importe_total"] = round(resumen_dict["importe_total"], 2)

        resumen_dict["propina_total"] += float(factura["propina"])
        resumen_dict["propina_total"] = round(resumen_dict["propina_total"], 2)

        resumen_dict["otros_rubros_total"] += float(
            factura["otrosRubrosTercerosTotal"])
        resumen_dict["otros_rubros_total"] = round(
            resumen_dict["otros_rubros_total"], 2)

    return resumen_dict


def processRetencion(comprobante):
    retencion_dict = {
        "retencionNumero": comprobante["comprobanteRetencion"]["infoTributaria"]["estab"] + "-" + comprobante["comprobanteRetencion"]["infoTributaria"]["ptoEmi"] + "-" + comprobante["comprobanteRetencion"]["infoTributaria"]["secuencial"],
        "retencionFecha": comprobante["comprobanteRetencion"]["infoCompRetencion"]["fechaEmision"],
        "impuestos": []
    }
    impuestos = comprobante["comprobanteRetencion"]["impuestos"]["impuesto"]
    if isinstance(impuestos, list):
        impuesto_dict = {}
        for impuesto in impuestos:
            impuesto_dict = {
                "codigo": impuesto["codigo"],
                "codigoRetencion": impuesto["codigoRetencion"],
                "baseImponible": impuesto["baseImponible"],
                "porcentajeRetener": impuesto["porcentajeRetener"],
                "valorRetenido": impuesto["valorRetenido"]
            }
            retencion_dict["impuestos"].append(impuesto_dict)
    else:
        impuesto = impuestos
        impuesto_dict = {
            "codigo": impuesto["codigo"],
            "codigoRetencion": impuesto["codigoRetencion"],
            "baseImponible": impuesto["baseImponible"],
            "porcentajeRetener": impuesto["porcentajeRetener"],
            "valorRetenido": impuesto["valorRetenido"]
        }
        retencion_dict["impuestos"].append(impuesto_dict)
    return retencion_dict


def computeRetenciones(retenciones_array):
    resumen_dict = {
        "total_retenido": 0
    }
    for retencion in retenciones_array:
        for impuesto in retencion["impuestos"]:
            resumen_dict["total_retenido"] += float(impuesto["valorRetenido"])
            resumen_dict["total_retenido"] = round(
                resumen_dict["total_retenido"], 2)
    return resumen_dict


def argumentControl():
    if len(sys.argv) < 2:
        print(
            "Uso del programa: python procesarCompRecSRI.py [mes]")
        exit(1)
    else:
        return


def main():
    argumentControl()
    month = sys.argv[1]
    folder = f'./comp/compRec/{month}'
    # procesar comprobantes recibidos
    files = os.listdir(folder)
    facturas = []
    retenciones = []
    for file in files:
        if file.split(".")[1] == "xml":
            comprobante = processXmlFile(folder, file)
            if "factura" in comprobante:
                facturas.append(processFactura(comprobante))
                printDict(facturas[len(facturas) - 1])

            if "comprobanteRetencion" in comprobante:
                retenciones.append(processRetencion(comprobante))
                #printDict(retenciones[len(retenciones) - 1])
        else:
            print(
                f'{file} no es un archivo .xml. El sistema solo es capaz de procesar archivos .xml')
            print("------------------------0------------------------")

    resumenFacturas = computeFacturas(facturas)
    print(
        f'------------------------Resumen facturas recibidas {month}------------------------')
    print("Resumen Facturas:")
    printDict(resumenFacturas)
    print(
        f'------------------------Resumen retenciones recibidas {month}------------------------')
    print("Resumen Retenciones:")
    resumenRetenciones = computeRetenciones(retenciones)
    printDict(resumenRetenciones)


def printDict(dict):
    json_print = json.dumps(dict, indent=2)
    print(json_print)
    print("------------------------0------------------------")


main()
